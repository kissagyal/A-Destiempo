# 📊 Resumen: Configurar Base de Datos en Otro PC

## 🎯 Proceso Rápido

### 1️⃣ Instalar MariaDB
- Descargar e instalar MariaDB desde [mariadb.org](https://mariadb.org/download/)
- Durante instalación: Anotar **password de root** y **puerto** (por defecto 3306)

### 2️⃣ Crear Base de Datos

Abre MariaDB (HeidiSQL, DBeaver, o línea de comandos) y ejecuta:

```sql
CREATE DATABASE adestiempo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3️⃣ Configurar Django

Edita `Destiempo/settings.py` y cambia estas líneas:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'adestiempo',
        'USER': 'root',              # ← Tu usuario de MariaDB
        'PASSWORD': 'tu_password',   # ← Tu password de MariaDB
        'HOST': '127.0.0.1',
        'PORT': '3306',              # ← Tu puerto (3306 por defecto)
        # ...
    }
}
```

### 4️⃣ Aplicar Migraciones

```bash
# Activar venv
.\venv\Scripts\Activate.ps1

# Crear todas las tablas
python manage.py migrate
```

Esto crea todas las tablas vacías en la base de datos.

### 5️⃣ Cargar Datos de Ejemplo (Opcional)

Si quieres datos de ejemplo (productos, usuarios de prueba):

```bash
python manage.py loaddata tasks/fixtures/all_data.json
```

Esto carga:
- Usuarios de prueba (cliente1, vendedor1)
- Productos de ejemplo
- Categorías, géneros, artistas
- Inventario de ejemplo

### 6️⃣ Crear Superusuario

```bash
python manage.py createsuperuser
```

Esto crea un usuario admin para acceder a `/admin/`

---

## 📋 Resumen en 3 Pasos

1. **Instalar MariaDB** → Crear BD `adestiempo`
2. **Configurar `settings.py`** → Poner tus credenciales
3. **Ejecutar migraciones** → `python manage.py migrate`

**Opcional:** Cargar datos de ejemplo con `loaddata`

---

## ✅ Verificación

Después de las migraciones, verifica en MariaDB:

```sql
USE adestiempo;
SHOW TABLES;
```

Deberías ver tablas como:
- `tasks_disco`
- `tasks_instrumento`
- `tasks_perfilusuario`
- `auth_user`
- etc.

---

## 🔑 Credenciales Necesarias

Anota estos datos durante la instalación:

- **Usuario MariaDB:** (generalmente `root`)
- **Password MariaDB:** (la que pusiste durante instalación)
- **Puerto:** (3306 por defecto, o el que configuraste)

---

## ⚠️ Importante

- **No necesitas copiar la base de datos completa** - Solo creas una nueva vacía
- **Las migraciones crean las tablas** automáticamente
- **Los fixtures cargan datos de ejemplo** (opcional)
- **Las imágenes no se incluyen** en los fixtures (se guardan en `media/`)

---

## 🎯 Flujo Completo

```
1. Instalar MariaDB
   ↓
2. Crear BD: CREATE DATABASE adestiempo;
   ↓
3. Editar settings.py (credenciales)
   ↓
4. python manage.py migrate (crea tablas)
   ↓
5. python manage.py loaddata fixtures/all_data.json (datos ejemplo)
   ↓
6. python manage.py createsuperuser (usuario admin)
   ↓
7. ¡Listo! Base de datos funcionando
```

---

**En resumen:** No copias la BD, solo creas una nueva vacía y Django la pobla con las migraciones y fixtures.

