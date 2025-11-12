# Generated migration to remove 'digital' format

from django.db import migrations, models


def remove_digital_format(apps, schema_editor):
    """Elimina el formato digital de discos e inventario"""
    Disco = apps.get_model('tasks', 'Disco')
    Inventario = apps.get_model('tasks', 'Inventario')
    
    # Eliminar inventarios con formato digital
    Inventario.objects.filter(formato_disco='digital').delete()
    
    # Actualizar discos con formato digital a CD (o puedes cambiarlos a otro formato)
    # Por ahora los cambiamos a CD
    discos_digital = Disco.objects.filter(formato='digital')
    for disco in discos_digital:
        disco.formato = 'cd'  # Cambiar a CD como formato por defecto
        disco.save()


def reverse_remove_digital_format(apps, schema_editor):
    """Reversa la eliminación del formato digital (no se puede revertir completamente)"""
    # No hay forma de revertir esto completamente ya que los datos se perdieron
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0010_add_categorias_instrumentos'),
    ]

    operations = [
        migrations.RunPython(remove_digital_format, reverse_remove_digital_format),
        # Actualizar las opciones del campo formato en el modelo
        migrations.AlterField(
            model_name='disco',
            name='formato',
            field=models.CharField(
                choices=[('vinilo', 'Vinilo'), ('cd', 'CD'), ('casete', 'Casete')],
                max_length=10
            ),
        ),
        migrations.AlterField(
            model_name='inventario',
            name='formato_disco',
            field=models.CharField(
                blank=True,
                choices=[('vinilo', 'Vinilo'), ('cd', 'CD'), ('casete', 'Casete')],
                max_length=10,
                null=True
            ),
        ),
    ]

