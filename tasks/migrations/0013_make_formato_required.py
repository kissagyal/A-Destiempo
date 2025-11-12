# Generated migration to make formato field required

from django.db import migrations, models


def set_default_formato(apps, schema_editor):
    """Establece un formato por defecto para discos que no tengan formato"""
    Disco = apps.get_model('tasks', 'Disco')
    # Establecer 'cd' como formato por defecto para discos sin formato
    Disco.objects.filter(formato__isnull=True).update(formato='cd')


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0012_make_formato_optional'),
    ]

    operations = [
        migrations.RunPython(set_default_formato, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='disco',
            name='formato',
            field=models.CharField(
                choices=[('vinilo', 'Vinilo'), ('cd', 'CD'), ('casete', 'Casete')],
                max_length=10
            ),
        ),
    ]




