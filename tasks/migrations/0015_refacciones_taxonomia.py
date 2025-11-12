from django.db import migrations, models
import django.db.models.deletion


def seed_refaccion_taxonomia(apps, schema_editor):
    CategoriaRefaccion = apps.get_model('tasks', 'CategoriaRefaccion')
    CompatibilidadGeneral = apps.get_model('tasks', 'CompatibilidadGeneral')

    categorias = [
        'Cuerdas',
        'Puentes / Tremolos',
        'Pastillas / Pickups',
        'Clavijas / Afinadores',
        'Pickguards / Golpeadores',
        'Potenciómetros / Electrónica',
        'Cables y Conectores',
        'Estuches / Fundas',
        'Correas (Straps)',
        'Golpeadores / Púas / Slides',
        'Parche de Batería',
        'Baquetas',
        'Atriles / Soportes',
        'Pedales / Efectos',
        'Micrófonos',
        'Sistemas Inalámbricos',
        'Audio / Interfaces',
        'Limpieza y Mantenimiento',
        'Accesorios Universales',
    ]
    for nombre in categorias:
        CategoriaRefaccion.objects.get_or_create(nombre=nombre, defaults={'descripcion': ''})

    compatibilidades = [
        'Guitarra Eléctrica',
        'Guitarra Acústica',
        'Bajo Eléctrico',
        'Batería / Percusión',
        'Teclado / Piano',
        'Micrófonos',
        'Sistemas Inalámbricos',
        'Audio (Cables, Conectividad)',
        'DJ / Controladores',
        'Estuches / Fundas',
        'Accesorios Universales',
    ]
    for nombre in compatibilidades:
        CompatibilidadGeneral.objects.get_or_create(nombre=nombre, defaults={'descripcion': ''})


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0014_herobanner'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompatibilidadGeneral',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=60, unique=True)),
                ('descripcion', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Compatibilidad General',
                'verbose_name_plural': 'Compatibilidades Generales',
                'ordering': ['nombre'],
            },
        ),
        migrations.AddField(
            model_name='refaccion',
            name='compatibilidad_general',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='refacciones', to='tasks.compatibilidadgeneral', help_text='Categoría general de compatibilidad (p. ej., Guitarra Eléctrica, Bajo, Universal)'),
        ),
        migrations.RunPython(seed_refaccion_taxonomia, migrations.RunPython.noop),
    ]


