from django.db import migrations, models
import tasks.models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0013_make_formato_required'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeroBanner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(upload_to=tasks.models.upload_to_hero_banners)),
                ('titulo', models.CharField(default='A Destiempo', max_length=150)),
                ('subtitulo', models.TextField(default='Descubre la mejor colección de discos, vinilos e instrumentos musicales. Donde la música cobra vida.')),
                ('boton_1_texto', models.CharField(default='Explorar Discos', max_length=80)),
                ('boton_1_url', models.CharField(blank=True, default='', max_length=200)),
                ('boton_2_texto', models.CharField(default='Ver Instrumentos', max_length=80)),
                ('boton_2_url', models.CharField(blank=True, default='', max_length=200)),
                ('actualizado', models.DateTimeField(auto_now=True)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('artista', models.OneToOneField(on_delete=models.CASCADE, related_name='hero_banner', to='tasks.artista')),
            ],
            options={
                'verbose_name': 'Hero Banner',
                'verbose_name_plural': 'Hero Banners',
            },
        ),
    ]




