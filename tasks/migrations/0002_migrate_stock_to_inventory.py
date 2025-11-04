# Generated manually for inventory migration

from django.db import migrations, models
from django.db.models import F


def create_principal_sucursal(apps, schema_editor):
    """Crear sucursal principal"""
    Sucursal = apps.get_model('tasks', 'Sucursal')
    Sucursal.objects.get_or_create(
        nombre='Principal',
        defaults={
            'ciudad': 'Ciudad Principal',
            'direccion': 'Dirección Principal',
            'activa': True
        }
    )


def migrate_disco_stock(apps, schema_editor):
    """Migrar stock de discos al inventario"""
    Disco = apps.get_model('tasks', 'Disco')
    Sucursal = apps.get_model('tasks', 'Sucursal')
    Inventario = apps.get_model('tasks', 'Inventario')
    
    sucursal_principal = Sucursal.objects.get(nombre='Principal')
    
    for disco in Disco.objects.all():
        Inventario.objects.create(
            producto_disco=disco,
            sucursal=sucursal_principal,
            stock_disponible=disco.stock,
            stock_reservado=0
        )


def migrate_instrumento_stock(apps, schema_editor):
    """Migrar stock de instrumentos al inventario"""
    Instrumento = apps.get_model('tasks', 'Instrumento')
    Sucursal = apps.get_model('tasks', 'Sucursal')
    Inventario = apps.get_model('tasks', 'Inventario')
    
    sucursal_principal = Sucursal.objects.get(nombre='Principal')
    
    for instrumento in Instrumento.objects.all():
        Inventario.objects.create(
            producto_instrumento=instrumento,
            sucursal=sucursal_principal,
            stock_disponible=instrumento.stock,
            stock_reservado=0
        )


def reverse_migrate_stock(apps, schema_editor):
    """Revertir migración - restaurar stock en productos"""
    Disco = apps.get_model('tasks', 'Disco')
    Instrumento = apps.get_model('tasks', 'Instrumento')
    Inventario = apps.get_model('tasks', 'Inventario')
    Sucursal = apps.get_model('tasks', 'Sucursal')
    
    sucursal_principal = Sucursal.objects.get(nombre='Principal')
    
    # Restaurar stock de discos
    for disco in Disco.objects.all():
        try:
            inventario = Inventario.objects.get(
                producto_disco=disco,
                sucursal=sucursal_principal
            )
            disco.stock = inventario.stock_disponible
            disco.save()
        except Inventario.DoesNotExist:
            disco.stock = 0
            disco.save()
    
    # Restaurar stock de instrumentos
    for instrumento in Instrumento.objects.all():
        try:
            inventario = Inventario.objects.get(
                producto_instrumento=instrumento,
                sucursal=sucursal_principal
            )
            instrumento.stock = inventario.stock_disponible
            instrumento.save()
        except Inventario.DoesNotExist:
            instrumento.stock = 0
            instrumento.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        # Crear modelos de inventario
        migrations.CreateModel(
            name='Sucursal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('ciudad', models.CharField(blank=True, max_length=100)),
                ('direccion', models.TextField(blank=True)),
                ('activa', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Sucursal',
                'verbose_name_plural': 'Sucursales',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Inventario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_disponible', models.PositiveIntegerField(default=0)),
                ('stock_reservado', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('producto_disco', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='inventario_disco', to='tasks.disco')),
                ('producto_instrumento', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='inventario_instrumento', to='tasks.instrumento')),
                ('sucursal', models.ForeignKey(on_delete=models.deletion.CASCADE, to='tasks.sucursal')),
            ],
            options={
                'verbose_name': 'Inventario',
                'verbose_name_plural': 'Inventarios',
            },
        ),
        migrations.CreateModel(
            name='InventarioMovimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('entrada', 'Entrada'), ('salida', 'Salida'), ('ajuste', 'Ajuste'), ('reserva', 'Reserva'), ('liberacion', 'Liberación de Reserva')], max_length=20)),
                ('cantidad', models.IntegerField()),
                ('motivo', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('producto_disco', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='movimientos_disco', to='tasks.disco')),
                ('producto_instrumento', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='movimientos_instrumento', to='tasks.instrumento')),
                ('sucursal', models.ForeignKey(on_delete=models.deletion.CASCADE, to='tasks.sucursal')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, to='auth.user')),
            ],
            options={
                'verbose_name': 'Movimiento de Inventario',
                'verbose_name_plural': 'Movimientos de Inventario',
                'ordering': ['-created_at'],
            },
        ),
        
        # Agregar constraints
        migrations.AddConstraint(
            model_name='inventario',
            constraint=models.UniqueConstraint(fields=('producto_disco', 'sucursal'), name='unique_disco_sucursal'),
        ),
        migrations.AddConstraint(
            model_name='inventario',
            constraint=models.UniqueConstraint(fields=('producto_instrumento', 'sucursal'), name='unique_instrumento_sucursal'),
        ),
        migrations.AddConstraint(
            model_name='inventario',
            constraint=models.CheckConstraint(check=models.Q(('producto_disco__isnull', False), ('producto_instrumento__isnull', True)) | models.Q(('producto_disco__isnull', True), ('producto_instrumento__isnull', False)), name='inventario_un_solo_producto'),
        ),
        migrations.AddConstraint(
            model_name='inventariomovimiento',
            constraint=models.CheckConstraint(check=models.Q(('producto_disco__isnull', False), ('producto_instrumento__isnull', True)) | models.Q(('producto_disco__isnull', True), ('producto_instrumento__isnull', False)), name='movimiento_un_solo_producto'),
        ),
        
        # Migrar datos
        migrations.RunPython(create_principal_sucursal, reverse_migrate_stock),
        migrations.RunPython(migrate_disco_stock, reverse_migrate_stock),
        migrations.RunPython(migrate_instrumento_stock, reverse_migrate_stock),
    ]
