from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum
import os

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
    año_lanzamiento = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2025)])
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
    """Inventario por producto y sucursal"""
    producto_disco = models.ForeignKey(Disco, on_delete=models.CASCADE, null=True, blank=True, related_name='inventario_disco')
    producto_instrumento = models.ForeignKey(Instrumento, on_delete=models.CASCADE, null=True, blank=True, related_name='inventario_instrumento')
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    stock_disponible = models.PositiveIntegerField(default=0)
    stock_reservado = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'
        unique_together = [
            ['producto_disco', 'sucursal'],
            ['producto_instrumento', 'sucursal']
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(producto_disco__isnull=False, producto_instrumento__isnull=True) |
                      models.Q(producto_disco__isnull=True, producto_instrumento__isnull=False),
                name='inventario_un_solo_producto'
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

def get_stock_total_disco(disco):
    """Obtiene el stock total de un disco en todas las sucursales"""
    return Inventario.objects.filter(
        producto_disco=disco
    ).aggregate(total=Sum('stock_disponible'))['total'] or 0

def get_stock_total_instrumento(instrumento):
    """Obtiene el stock total de un instrumento en todas las sucursales"""
    return Inventario.objects.filter(
        producto_instrumento=instrumento
    ).aggregate(total=Sum('stock_disponible'))['total'] or 0
