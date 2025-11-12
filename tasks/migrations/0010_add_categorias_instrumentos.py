# Generated migration to add general instrument categories

from django.db import migrations


def add_categorias_instrumentos(apps, schema_editor):
    """Añade categorías generales para instrumentos"""
    CategoriaInstrumento = apps.get_model('tasks', 'CategoriaInstrumento')
    
    categorias = [
        {'nombre': 'Guitarras', 'descripcion': 'Guitarras eléctricas, acústicas y clásicas', 'tipo': 'instrumento'},
        {'nombre': 'Bajos', 'descripcion': 'Bajos eléctricos y acústicos', 'tipo': 'instrumento'},
        {'nombre': 'Baterías', 'descripcion': 'Baterías acústicas y electrónicas', 'tipo': 'instrumento'},
        {'nombre': 'Teclados', 'descripcion': 'Pianos, sintetizadores y teclados', 'tipo': 'instrumento'},
        {'nombre': 'Instrumentos de Viento', 'descripcion': 'Saxofones, trompetas, flautas y más', 'tipo': 'instrumento'},
        {'nombre': 'Instrumentos de Cuerda', 'descripcion': 'Violines, violas, cellos y más', 'tipo': 'instrumento'},
        {'nombre': 'Percusión', 'descripcion': 'Instrumentos de percusión diversos', 'tipo': 'instrumento'},
        {'nombre': 'Amplificadores', 'descripcion': 'Amplificadores para guitarras, bajos y más', 'tipo': 'accesorio'},
        {'nombre': 'Efectos y Pedales', 'descripcion': 'Pedales de efectos y procesadores', 'tipo': 'accesorio'},
        {'nombre': 'Micrófonos', 'descripcion': 'Micrófonos para voces e instrumentos', 'tipo': 'accesorio'},
        {'nombre': 'Cables y Conectores', 'descripcion': 'Cables de audio, instrumentales y conectores', 'tipo': 'accesorio'},
        {'nombre': 'Accesorios', 'descripcion': 'Correas, afinadores, fundas y otros accesorios', 'tipo': 'accesorio'},
    ]
    
    for categoria_data in categorias:
        # Solo crear si no existe
        if not CategoriaInstrumento.objects.filter(nombre=categoria_data['nombre']).exists():
            CategoriaInstrumento.objects.create(**categoria_data)


def remove_categorias_instrumentos(apps, schema_editor):
    """Elimina las categorías añadidas (reversible)"""
    CategoriaInstrumento = apps.get_model('tasks', 'CategoriaInstrumento')
    
    nombres = [
        'Guitarras', 'Bajos', 'Baterías', 'Teclados', 
        'Instrumentos de Viento', 'Instrumentos de Cuerda', 'Percusión',
        'Amplificadores', 'Efectos y Pedales', 'Micrófonos',
        'Cables y Conectores', 'Accesorios'
    ]
    
    CategoriaInstrumento.objects.filter(nombre__in=nombres).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_categoriarefaccion_pedido_refaccion_itempedido_and_more'),
    ]

    operations = [
        migrations.RunPython(add_categorias_instrumentos, remove_categorias_instrumentos),
    ]




