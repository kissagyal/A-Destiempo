from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import os

class PerfilUsuario(models.Model):
    TIPOS_USUARIO = [
        ('usuario', 'Usuario'),
        ('empleado', 'Empleado'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(max_length=10, choices=TIPOS_USUARIO, default='usuario')
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

class CategoriaInstrumento(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    
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
