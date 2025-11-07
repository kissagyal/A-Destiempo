from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum
from django.core.exceptions import ValidationError
import os
from datetime import datetime

class PerfilUsuario(models.Model):
    TIPOS_USUARIO = [
        ('cliente', 'Cliente'),
        ('vendedor', 'Vendedor'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(max_length=10, choices=TIPOS_USUARIO, default='cliente')
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f"{self.user.username} - {self.tipo_usuario}"

class Genero(models.Model):
    """Género musical"""
    nombre = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = 'Género'
        verbose_name_plural = 'Géneros'
    
    def __str__(self):
        return self.nombre

class Artista(models.Model):
    nombre = models.CharField(max_length=100)
    biografia = models.TextField(blank=True)
    foto = models.ImageField(upload_to='artistas/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Artista'
        verbose_name_plural = 'Artistas'
    
    def __str__(self):
        return self.nombre

def upload_to_discos(instance, filename):
    return os.path.join('discos', instance.artista.nombre, filename)

class Disco(models.Model):
    FORMATOS = [
        ('vinilo', 'Vinilo'),
        ('cd', 'CD'),
        ('digital', 'Digital'),
        ('casete', 'Casete'),
    ]
    
    titulo = models.CharField(max_length=200)
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE, related_name='discos')
    genero = models.ForeignKey(Genero, on_delete=models.SET_NULL, null=True, blank=True)
    año_lanzamiento = models.IntegerField(
        validators=[
            MinValueValidator(1950, message='El año debe ser mayor o igual a 1950'),
            MaxValueValidator(datetime.now().year, message=f'El año no puede ser mayor a {datetime.now().year}')
        ]
    )
    formato = models.CharField(max_length=10, choices=FORMATOS)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    descripcion = models.TextField(blank=True)
    portada = models.ImageField(upload_to=upload_to_discos, blank=True, null=True)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Disco'
        verbose_name_plural = 'Discos'
        ordering = ['-fecha_agregado']
    
    def __str__(self):
        return f"{self.artista.nombre} - {self.titulo}"
    
    @property
    def stock_total(self):
        """Stock total en todas las sucursales (compatibilidad)"""
        return get_stock_total_disco(self)
    
    def tiene_stock(self):
        """Verifica si tiene stock disponible"""
        return self.stock_total > 0

class CategoriaInstrumento(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    TIPOS = [
        ('instrumento', 'Instrumento'),
        ('refaccion', 'Refacción'),
        ('accesorio', 'Accesorio'),
    ]
    tipo = models.CharField(max_length=12, choices=TIPOS, default='instrumento')
    
    class Meta:
        verbose_name = 'Categoría de Instrumento'
        verbose_name_plural = 'Categorías de Instrumentos'
    
    def __str__(self):
        return self.nombre

def upload_to_instrumentos(instance, filename):
    return os.path.join('instrumentos', instance.categoria.nombre, filename)

class Instrumento(models.Model):
    ESTADOS = [
        ('nuevo', 'Nuevo'),
        ('usado', 'Usado'),
        ('vintage', 'Vintage'),
    ]
    
    nombre = models.CharField(max_length=200)
    marca = models.CharField(max_length=100)
    categoria = models.ForeignKey(CategoriaInstrumento, on_delete=models.CASCADE, related_name='instrumentos')
    modelo = models.CharField(max_length=100, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADOS)
    stock = models.PositiveIntegerField(default=0)
    descripcion = models.TextField(blank=True)
    imagen_principal = models.ImageField(upload_to=upload_to_instrumentos, blank=True, null=True)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Instrumento'
        verbose_name_plural = 'Instrumentos'
        ordering = ['-fecha_agregado']
    
    def __str__(self):
        return f"{self.marca} {self.nombre}"
    
    @property
    def stock_total(self):
        """Stock total en todas las sucursales (compatibilidad)"""
        return get_stock_total_instrumento(self)
    
    def tiene_stock(self):
        """Verifica si tiene stock disponible"""
        return self.stock_total > 0

# ===========================================
# MODELOS DE INVENTARIO MULTI-SUCURSAL
# ===========================================

class Sucursal(models.Model):
    """Modelo para sucursales/tiendas"""
    nombre = models.CharField(max_length=100, unique=True)
    ciudad = models.CharField(max_length=100, blank=True)
    direccion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Inventario(models.Model):
    """Inventario por producto, formato (para discos) y sucursal"""
    producto_disco = models.ForeignKey(Disco, on_delete=models.CASCADE, null=True, blank=True, related_name='inventario_disco')
    producto_instrumento = models.ForeignKey(Instrumento, on_delete=models.CASCADE, null=True, blank=True, related_name='inventario_instrumento')
    # Para discos: formato específico (vinilo, cd, digital, casete)
    # Para instrumentos: siempre null
    formato_disco = models.CharField(max_length=10, choices=Disco.FORMATOS, null=True, blank=True)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    stock_disponible = models.PositiveIntegerField(default=0)
    stock_reservado = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'
        unique_together = [
            ['producto_disco', 'formato_disco', 'sucursal'],
            ['producto_instrumento', 'sucursal']
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(producto_disco__isnull=False, producto_instrumento__isnull=True) |
                      models.Q(producto_disco__isnull=True, producto_instrumento__isnull=False),
                name='inventario_un_solo_producto'
            ),
            models.CheckConstraint(
                check=models.Q(producto_disco__isnull=False, formato_disco__isnull=False) |
                      models.Q(producto_disco__isnull=True),
                name='formato_solo_para_discos'
            )
        ]
    
    def __str__(self):
        producto = self.producto_disco or self.producto_instrumento
        return f"{producto} - {self.sucursal.nombre} ({self.stock_disponible})"
    
    @property
    def producto(self):
        """Retorna el producto (disco o instrumento)"""
        return self.producto_disco or self.producto_instrumento
    
    @property
    def stock_total(self):
        """Stock total (disponible + reservado)"""
        return self.stock_disponible + self.stock_reservado

class InventarioMovimiento(models.Model):
    """Histórico de movimientos de inventario"""
    TIPOS_MOVIMIENTO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
        ('reserva', 'Reserva'),
        ('liberacion', 'Liberación de Reserva'),
    ]
    
    producto_disco = models.ForeignKey(Disco, on_delete=models.CASCADE, null=True, blank=True, related_name='movimientos_disco')
    producto_instrumento = models.ForeignKey(Instrumento, on_delete=models.CASCADE, null=True, blank=True, related_name='movimientos_instrumento')
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPOS_MOVIMIENTO)
    cantidad = models.IntegerField()  # Positivo para entrada, negativo para salida
    motivo = models.TextField(blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(producto_disco__isnull=False, producto_instrumento__isnull=True) |
                      models.Q(producto_disco__isnull=True, producto_instrumento__isnull=False),
                name='movimiento_un_solo_producto'
            )
        ]
    
    def __str__(self):
        producto = self.producto_disco or self.producto_instrumento
        return f"{producto} - {self.sucursal.nombre} - {self.get_tipo_display()} ({self.cantidad})"
    
    @property
    def producto(self):
        """Retorna el producto (disco o instrumento)"""
        return self.producto_disco or self.producto_instrumento

# ===========================================
# MÉTODOS DE STOCK PARA COMPATIBILIDAD
# ===========================================

def get_stock_total_disco(disco, formato=None):
    """Obtiene el stock total de un disco en todas las sucursales
    Si se especifica formato, retorna solo el stock de ese formato"""
    query = Inventario.objects.filter(producto_disco=disco)
    if formato:
        query = query.filter(formato_disco=formato)
    return query.aggregate(total=Sum('stock_disponible'))['total'] or 0

def get_stock_total_instrumento(instrumento):
    """Obtiene el stock total de un instrumento en todas las sucursales"""
    return Inventario.objects.filter(
        producto_instrumento=instrumento
    ).aggregate(total=Sum('stock_disponible'))['total'] or 0

class Favorito(models.Model):
    """Modelo para guardar productos favoritos de los usuarios"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoritos')
    disco = models.ForeignKey(Disco, on_delete=models.CASCADE, null=True, blank=True, related_name='favoritos')
    instrumento = models.ForeignKey(Instrumento, on_delete=models.CASCADE, null=True, blank=True, related_name='favoritos')
    refaccion = models.ForeignKey('Refaccion', on_delete=models.CASCADE, null=True, blank=True, related_name='favoritos')
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'
        unique_together = [
            ('usuario', 'disco'),
            ('usuario', 'instrumento'),
            ('usuario', 'refaccion'),
        ]
    
    def __str__(self):
        if self.disco:
            return f"{self.usuario.username} - {self.disco.titulo}"
        elif self.instrumento:
            return f"{self.usuario.username} - {self.instrumento.nombre}"
        elif self.refaccion:
            return f"{self.usuario.username} - {self.refaccion.nombre}"
        return f"{self.usuario.username} - Favorito"

# ===========================================
# MODELO DE REFACCIONES
# ===========================================

class CategoriaRefaccion(models.Model):
    """Categorías para refacciones"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Categoría de Refacción'
        verbose_name_plural = 'Categorías de Refacciones'
    
    def __str__(self):
        return self.nombre

def upload_to_refacciones(instance, filename):
    return os.path.join('refacciones', instance.categoria.nombre, filename)

class Refaccion(models.Model):
    """Modelo para refacciones de instrumentos"""
    nombre = models.CharField(max_length=200)
    marca = models.CharField(max_length=100)
    categoria = models.ForeignKey(CategoriaRefaccion, on_delete=models.CASCADE, related_name='refacciones')
    modelo_compatible = models.CharField(max_length=200, blank=True, help_text="Modelos de instrumentos con los que es compatible")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    descripcion = models.TextField(blank=True)
    imagen_principal = models.ImageField(upload_to=upload_to_refacciones, blank=True, null=True)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Refacción'
        verbose_name_plural = 'Refacciones'
        ordering = ['-fecha_agregado']
    
    def __str__(self):
        return f"{self.marca} {self.nombre}"
    
    @property
    def stock_total(self):
        """Stock total en todas las sucursales (compatibilidad)"""
        return get_stock_total_refaccion(self) if hasattr(self, 'get_stock_total_refaccion') else self.stock
    
    def tiene_stock(self):
        """Verifica si tiene stock disponible"""
        return self.stock_total > 0

# ===========================================
# MODELOS DE PEDIDOS Y FACTURACIÓN
# ===========================================

class Pedido(models.Model):
    """Modelo para pedidos de clientes"""
    ESTADOS_PEDIDO = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('en_camino', 'En Camino'),
        ('enviado', 'Enviado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    numero_pedido = models.CharField(max_length=20, unique=True, editable=False)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='pendiente')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Información de envío
    nombre_completo = models.CharField(max_length=200)
    direccion = models.TextField()
    ciudad = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20, blank=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Información de pago (simulada)
    metodo_pago = models.CharField(max_length=50, default='transferencia', help_text="Método de pago simulado")
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    
    # Facturación
    factura_enviada = models.BooleanField(default=False)
    fecha_factura_enviada = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_pedido']
    
    def __str__(self):
        return f"Pedido #{self.numero_pedido} - {self.cliente.username}"
    
    def save(self, *args, **kwargs):
        if not self.numero_pedido:
            # Generar número de pedido único
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d')
            last_pedido = Pedido.objects.filter(numero_pedido__startswith=timestamp).order_by('-numero_pedido').first()
            if last_pedido:
                try:
                    last_num = int(last_pedido.numero_pedido.split('-')[-1])
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            self.numero_pedido = f"{timestamp}-{new_num:04d}"
        super().save(*args, **kwargs)
    
    def calcular_total(self):
        """Calcula el total del pedido sumando los items"""
        total = sum(item.subtotal for item in self.items.all())
        self.subtotal = total
        self.impuestos = total * 0.16  # IVA 16%
        self.total = self.subtotal + self.impuestos
        self.save(update_fields=['subtotal', 'impuestos', 'total'])
        return self.total

class ItemPedido(models.Model):
    """Items individuales de un pedido"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    disco = models.ForeignKey(Disco, on_delete=models.SET_NULL, null=True, blank=True)
    instrumento = models.ForeignKey(Instrumento, on_delete=models.SET_NULL, null=True, blank=True)
    refaccion = models.ForeignKey(Refaccion, on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Items de Pedido'
    
    def __str__(self):
        producto = self.disco or self.instrumento or self.refaccion
        if producto:
            return f"{producto} x{self.cantidad}"
        return f"Item {self.id}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

def get_stock_total_refaccion(refaccion):
    """Obtiene el stock total de una refacción en todas las sucursales"""
    # Por ahora retornar stock directo, se puede expandir con inventario multi-sucursal
    return refaccion.stock
