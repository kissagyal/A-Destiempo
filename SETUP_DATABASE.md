# 📊 Guía de Base de Datos - A Destiempo

## 🗄️ Configuración de MariaDB

### 1. Crear la Base de Datos

```sql
CREATE DATABASE adestiempo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Configurar Usuario (Opcional)

```sql
CREATE USER 'adestiempo_user'@'localhost' IDENTIFIED BY 'tu_password';
GRANT ALL PRIVILEGES ON adestiempo.* TO 'adestiempo_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Configurar Django

Edita `Destiempo/settings.py` y ajusta las credenciales:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'adestiempo',
        'USER': 'root',  # o 'adestiempo_user'
        'PASSWORD': '',  # tu password
        'HOST': '127.0.0.1',
        'PORT': '3309',  # ajusta según tu configuración
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
        },
    }
}
```

---

## 🚀 Configuración Inicial (Base de Datos Vacía)

### Paso 1: Aplicar Migraciones

```bash
# Activar entorno virtual (Windows)
.\venv\Scripts\Activate.ps1

# Aplicar migraciones
python manage.py migrate
```

### Paso 2: Crear Superusuario

```bash
python manage.py createsuperuser
```

### Paso 3: Cargar Datos de Ejemplo (Opcional)

Si tienes fixtures guardados:

```bash
# Cargar todos los fixtures
python manage.py loaddata tasks/fixtures/*.json

# O cargar uno por uno
python manage.py loaddata tasks/fixtures/genero.json
python manage.py loaddata tasks/fixtures/artista.json
python manage.py loaddata tasks/fixtures/disco.json
# ... etc
```

---

## 📤 Exportar Datos de la Base de Datos

### Método 1: Script Automático (Recomendado)

```bash
python exportar_datos.py
```

Este script exporta todos los modelos a `tasks/fixtures/` en formato JSON.

### Método 2: Comando Manual de Django

```bash
# Exportar un modelo específico
python manage.py dumpdata tasks.Disco > tasks/fixtures/disco.json

# Exportar todos los modelos de tasks
python manage.py dumpdata tasks > tasks/fixtures/all_data.json

# Exportar con formato legible
python manage.py dumpdata tasks --indent 2 > tasks/fixtures/all_data.json

# Exportar con claves naturales (para relaciones)
python manage.py dumpdata tasks --natural-foreign --natural-primary > tasks/fixtures/all_data.json
```

### Exportar Modelos Específicos

```bash
# Usuarios y perfiles
python manage.py dumpdata auth.User tasks.PerfilUsuario > tasks/fixtures/usuarios.json

# Catálogo completo
python manage.py dumpdata tasks.Genero tasks.Artista tasks.Disco > tasks/fixtures/catalogo_discos.json

# Instrumentos
python manage.py dumpdata tasks.CategoriaInstrumento tasks.Instrumento > tasks/fixtures/instrumentos.json

# Inventario
python manage.py dumpdata tasks.Sucursal tasks.Inventario tasks.InventarioMovimiento > tasks/fixtures/inventario.json
```

---

## 📥 Importar Datos a la Base de Datos

### Cargar Fixtures

```bash
# Cargar un fixture específico
python manage.py loaddata tasks/fixtures/disco.json

# Cargar todos los fixtures en orden
python manage.py loaddata tasks/fixtures/genero.json
python manage.py loaddata tasks/fixtures/artista.json
python manage.py loaddata tasks/fixtures/disco.json
# ... etc

# O cargar todos a la vez (si están en un solo archivo)
python manage.py loaddata tasks/fixtures/all_data.json
```

**⚠️ Importante:** Carga los fixtures en orden de dependencias:
1. `genero.json`
2. `artista.json`
3. `categoriainstrumento.json`
4. `sucursal.json`
5. `user.json`
6. `perfilusuario.json`
7. `disco.json`
8. `instrumento.json`
9. `inventario.json`
10. `inventariomovimiento.json`

---

## 🔄 Backup y Restore de MariaDB

### Backup Completo (SQL)

```bash
# Exportar toda la base de datos
mysqldump -u root -p adestiempo > backup_adestiempo.sql

# Exportar solo estructura
mysqldump -u root -p --no-data adestiempo > estructura_adestiempo.sql

# Exportar solo datos
mysqldump -u root -p --no-create-info adestiempo > datos_adestiempo.sql
```

### Restore desde SQL

```bash
mysql -u root -p adestiempo < backup_adestiempo.sql
```

---

## 📋 Mejores Prácticas para Git

### ✅ SÍ Subir a Git:
- ✅ Migraciones (`tasks/migrations/*.py`)
- ✅ Fixtures de ejemplo (`tasks/fixtures/*.json`)
- ✅ Scripts de exportación (`exportar_datos.py`)
- ✅ Documentación (`SETUP_DATABASE.md`)

### ❌ NO Subir a Git:
- ❌ Base de datos completa (`.sql`, `.db`)
- ❌ Dumps de producción
- ❌ Credenciales de producción
- ❌ Archivos de configuración con passwords

### Archivos ya Ignorados (`.gitignore`):
- `db.sqlite3`
- `db.json`
- `*.sql`
- `.env`
- `venv/`

---

## 🧪 Crear Datos de Prueba

### Usuarios de Prueba

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from tasks.models import PerfilUsuario

# Crear cliente
cliente = User.objects.create_user('cliente1', password='cliente123')
PerfilUsuario.objects.create(user=cliente, tipo_usuario='cliente')

# Crear vendedor
vendedor = User.objects.create_user('vendedor1', password='vendedor123')
PerfilUsuario.objects.create(user=vendedor, tipo_usuario='vendedor')
```

### Crear Datos de Ejemplo desde el Admin

1. Inicia sesión como superusuario
2. Accede a `/admin/`
3. Crea géneros, artistas, categorías, etc.
4. Crea discos e instrumentos
5. Exporta con `python exportar_datos.py`

---

## 🔧 Solución de Problemas

### Error: "Unknown column 'tasks_categoriainstrumento.tipo'"
**Solución:** Aplica las migraciones pendientes:
```bash
python manage.py migrate
```

### Error: "Table doesn't exist"
**Solución:** Crea la base de datos y aplica migraciones:
```bash
python manage.py migrate
```

### Error: "Access denied for user"
**Solución:** Verifica las credenciales en `settings.py` y que el usuario tenga permisos:
```sql
GRANT ALL PRIVILEGES ON adestiempo.* TO 'tu_usuario'@'localhost';
FLUSH PRIVILEGES;
```

---

## 📝 Notas

- Las imágenes se guardan en `media/` (no se suben a Git)
- Los fixtures JSON son solo para datos de ejemplo
- Para producción, usa backups SQL completos
- Mantén un `.env.example` con la estructura de variables (sin valores reales)

