from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import PerfilUsuario, Disco, Instrumento, Artista, Genero, CategoriaInstrumento, Inventario, Sucursal


@receiver(post_save, sender=PerfilUsuario)
def asignar_permisos_vendedor(sender, instance, created, **kwargs):
    """
    Asigna permisos de admin automáticamente a los vendedores
    """
    if instance.tipo_usuario == 'vendedor':
        user = instance.user
        user.is_staff = True
        user.save()
        
        # Obtener ContentTypes de los modelos relevantes
        disco_ct = ContentType.objects.get_for_model(Disco)
        instrumento_ct = ContentType.objects.get_for_model(Instrumento)
        artista_ct = ContentType.objects.get_for_model(Artista)
        genero_ct = ContentType.objects.get_for_model(Genero)
        categoria_ct = ContentType.objects.get_for_model(CategoriaInstrumento)
        inventario_ct = ContentType.objects.get_for_model(Inventario)
        sucursal_ct = ContentType.objects.get_for_model(Sucursal)
        
        # Obtener todos los permisos para estos modelos
        permisos = Permission.objects.filter(
            content_type__in=[
                disco_ct, instrumento_ct, artista_ct, genero_ct,
                categoria_ct, inventario_ct, sucursal_ct
            ]
        )
        
        # Asignar permisos al usuario
        user.user_permissions.set(permisos)
        
    elif instance.tipo_usuario == 'cliente':
        # Los clientes no tienen acceso al admin
        user = instance.user
        user.is_staff = False
        user.user_permissions.clear()
        user.save()

