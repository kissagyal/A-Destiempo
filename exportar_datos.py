"""
Script para exportar datos de la base de datos MariaDB a fixtures JSON.
Esto permite tener datos de ejemplo para subir a Git y compartir.

Uso:
    python exportar_datos.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Destiempo.settings')
django.setup()

from django.core.management import call_command

def exportar_datos():
    """Exporta todos los datos a fixtures JSON"""
    
    # Crear directorio de fixtures si no existe
    fixtures_dir = 'tasks/fixtures'
    if not os.path.exists(fixtures_dir):
        os.makedirs(fixtures_dir)
    
    print("📦 Exportando datos a fixtures...")
    print("=" * 50)
    
    # Modelos a exportar (en orden de dependencias)
    modelos = [
        'auth.User',
        'tasks.PerfilUsuario',
        'tasks.Genero',
        'tasks.Artista',
        'tasks.CategoriaInstrumento',
        'tasks.Sucursal',
        'tasks.Disco',
        'tasks.Instrumento',
        'tasks.Inventario',
        'tasks.InventarioMovimiento',
    ]
    
    for modelo in modelos:
        app_label, model_name = modelo.split('.')
        output_file = f'{fixtures_dir}/{model_name.lower()}.json'
        
        try:
            print(f"📤 Exportando {modelo}...", end=' ')
            call_command('dumpdata', modelo, 
                        output=output_file,
                        indent=2,
                        natural_foreign=True,
                        natural_primary=True)
            print("✅")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("=" * 50)
    print("✅ Exportación completada!")
    print(f"📁 Fixtures guardados en: {fixtures_dir}/")
    print("\nPara cargar estos datos en otra base de datos:")
    print("  python manage.py loaddata tasks/fixtures/*.json")

if __name__ == '__main__':
    exportar_datos()

