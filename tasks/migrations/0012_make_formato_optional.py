# Generated migration to make formato field optional

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0011_remove_formato_digital'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disco',
            name='formato',
            field=models.CharField(
                blank=True,
                choices=[('vinilo', 'Vinilo'), ('cd', 'CD'), ('casete', 'Casete')],
                help_text='Formato principal (opcional, se determina por el stock disponible)',
                max_length=10,
                null=True
            ),
        ),
    ]




