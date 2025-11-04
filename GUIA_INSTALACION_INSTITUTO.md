# 🚀 Guía de Instalación - A Destiempo (PC del Instituto)

Esta guía te ayudará a configurar el proyecto **A Destiempo** desde cero en otro PC (por ejemplo, del instituto).

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

1. **Python 3.13** (o superior) - [Descargar Python](https://www.python.org/downloads/)
2. **MariaDB** (o MySQL) - [Descargar MariaDB](https://mariadb.org/download/)
3. **Git** (opcional, para clonar) - [Descargar Git](https://git-scm.com/downloads)

---

## 🔧 Paso 1: Clonar o Descargar el Proyecto

### Opción A: Clonar desde GitHub (si está subido)

```bash
git clone https://github.com/tu-usuario/a-destiempo.git
cd a-destiempo
```

### Opción B: Descargar ZIP y Extraer

1. Descarga el proyecto como ZIP desde GitHub
2. Extrae el archivo en una carpeta (ej: `C:\Users\TuUsuario\Desktop\A Destiempo`)
3. Abre PowerShell o CMD en esa carpeta

---

## 🐍 Paso 2: Crear Entorno Virtual

Abre PowerShell o CMD en la carpeta del proyecto:

```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Si PowerShell no permite ejecutar scripts, ejecuta esto primero:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# O usar CMD (Windows)
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

**✅ Verificación:** Deberías ver `(venv)` al inicio de tu línea de comandos.

---

## 📦 Paso 3: Instalar Dependencias

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

Esto instalará:
- Django 5.2.7
- mysqlclient 2.2.7
- Pillow 12.0.0
- Y otras dependencias

**⚠️ Si tienes problemas con `mysqlclient`:**
- En Windows, puede necesitar Visual C++ Build Tools
- Alternativa temporal: usar `pip install mysqlclient` o instalar desde wheel

---

## 🗄️ Paso 4: Instalar y Configurar MariaDB

### 4.1. Instalar MariaDB

1. Descarga e instala MariaDB desde [mariadb.org](https://mariadb.org/download/)
2. Durante la instalación, configura:
   - **Puerto:** 3306 (o el que prefieras, anótalo)
   - **Password para root:** (anótalo, lo necesitarás)

### 4.2. Crear Base de Datos

Abre MariaDB (o HeidiSQL, DBeaver, o línea de comandos):

```sql
-- Conectar como root
mysql -u root -p

-- Crear base de datos
CREATE DATABASE adestiempo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Verificar
SHOW DATABASES;
```

**O usando HeidiSQL/DBeaver:**
1. Conecta a MariaDB
2. Crea nueva base de datos: `adestiempo`
3. Configura charset: `utf8mb4`
4. Collation: `utf8mb4_unicode_ci`

---

## ⚙️ Paso 5: Configurar Django

### 5.1. Editar `Destiempo/settings.py`

Abre el archivo `Destiempo/settings.py` y busca la sección `DATABASES`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'adestiempo',
        'USER': 'root',              # Tu usuario de MariaDB
        'PASSWORD': 'tu_password',   # Tu contraseña de MariaDB
        'HOST': '127.0.0.1',
        'PORT': '3306',              # El puerto que configuraste (3306 por defecto)
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
        },
        'CONN_MAX_AGE': 60,
    }
}
```

**⚠️ Cambia:**
- `USER`: Tu usuario de MariaDB (generalmente `root`)
- `PASSWORD`: Tu contraseña de MariaDB
- `PORT`: El puerto que configuraste (3306 por defecto, o 3309 si usas otro)

### 5.2. Verificar Configuración

```bash
python manage.py check
```

Si todo está bien, verás: `System check identified no issues (0 silenced).`

---

## 🗄️ Paso 6: Aplicar Migraciones

Con el entorno virtual activado y la base de datos creada:

```bash
python manage.py migrate
```

Esto creará todas las tablas en la base de datos `adestiempo`.

**✅ Verificación:** Abre MariaDB y verifica que las tablas se hayan creado:
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

## 👤 Paso 7: Crear Superusuario

```bash
python manage.py createsuperuser
```

Ingresa:
- **Username:** (el que prefieras)
- **Email:** (opcional)
- **Password:** (anótalo, lo necesitarás)

**✅ Este usuario podrá acceder a `/admin/` y al panel de vendedor.**

---

## 📥 Paso 8: Cargar Datos de Ejemplo

Si el proyecto incluye fixtures (archivos JSON en `tasks/fixtures/`):

```bash
# Cargar todos los datos
python manage.py loaddata tasks/fixtures/all_data.json

# O si hay archivos separados, cargar en orden:
python manage.py loaddata tasks/fixtures/genero.json
python manage.py loaddata tasks/fixtures/artista.json
python manage.py loaddata tasks/fixtures/disco.json
python manage.py loaddata tasks/fixtures/instrumento.json
# ... etc
```

**✅ Verificación:** 
- Abre el admin: `http://127.0.0.1:8000/admin/`
- O la página principal: `http://127.0.0.1:8000/`
- Deberías ver productos de ejemplo

---

## 🚀 Paso 9: Ejecutar el Servidor

```bash
python manage.py runserver
```

Deberías ver:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

**✅ Abre tu navegador en:** `http://127.0.0.1:8000/`

---

## 🧪 Paso 10: Probar el Sistema

### 10.1. Credenciales de Prueba (si cargaste fixtures)

**Cliente:**
- Username: `cliente1`
- Password: `cliente123`

**Vendedor:**
- Username: `vendedor1`
- Password: `vendedor123`

### 10.2. Verificar Funcionalidades

1. **Como Visitante:**
   - Ver catálogo ✅
   - Intentar agregar al carrito → Debe pedir login ✅

2. **Como Cliente:**
   - Iniciar sesión con `cliente1`
   - Agregar productos al carrito ✅
   - Ver carrito ✅

3. **Como Vendedor:**
   - Iniciar sesión con `vendedor1`
   - Acceder a `/panel-empleado/` ✅
   - Crear/editar/eliminar productos ✅

---

## 🔧 Solución de Problemas Comunes

### Error: "ModuleNotFoundError: No module named 'MySQLdb'"

**Solución:**
```bash
# Asegúrate de estar en el venv
.\venv\Scripts\Activate.ps1

# Reinstalar mysqlclient
pip install mysqlclient

# Si falla, instala Visual C++ Build Tools o usa:
pip install pymysql
# Y en settings.py, cambia ENGINE a 'django.db.backends.mysql' con pymysql
```

### Error: "Access denied for user 'root'@'localhost'"

**Solución:**
1. Verifica las credenciales en `settings.py`
2. Verifica que MariaDB esté corriendo
3. Prueba conectarte manualmente:
```sql
mysql -u root -p
```

### Error: "Unknown database 'adestiempo'"

**Solución:**
```sql
-- Crea la base de datos
CREATE DATABASE adestiempo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Error: "Table doesn't exist"

**Solución:**
```bash
# Aplica las migraciones
python manage.py migrate
```

### Error: "Port 3306 already in use"

**Solución:**
1. Verifica qué proceso usa el puerto
2. Cambia el puerto en `settings.py` (ej: `'PORT': '3307'`)
3. O detén el proceso que usa el puerto

### Error en PowerShell: "cannot be loaded because running scripts is disabled"

**Solución:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Luego intenta activar el venv de nuevo.

---

## 📝 Checklist de Instalación

- [ ] Python 3.13+ instalado
- [ ] MariaDB instalado y corriendo
- [ ] Proyecto clonado/descargado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Base de datos `adestiempo` creada
- [ ] `settings.py` configurado con credenciales correctas
- [ ] Migraciones aplicadas (`python manage.py migrate`)
- [ ] Superusuario creado (`python manage.py createsuperuser`)
- [ ] Datos de ejemplo cargados (si aplica)
- [ ] Servidor corriendo (`python manage.py runserver`)
- [ ] Página principal accesible en `http://127.0.0.1:8000/`

---

## 🎯 Siguiente Paso

Una vez que todo funcione:

1. **Explora el catálogo:** `http://127.0.0.1:8000/discos/` y `/instrumentos/`
2. **Prueba como cliente:** Inicia sesión y agrega productos al carrito
3. **Prueba como vendedor:** Accede al panel y gestiona productos
4. **Lee la documentación:**
   - `README.md` - Información general
   - `RESUMEN_PERMISOS.md` - Permisos y roles
   - `SETUP_DATABASE.md` - Guía de base de datos

---

## 💡 Tips Adicionales

- **Imágenes:** Si faltan imágenes, se mostrarán iconos por defecto. Las imágenes se guardan en `media/`
- **Backup:** Exporta datos regularmente con `python manage.py dumpdata tasks > backup.json`
- **Logs:** Los errores se muestran en la consola cuando `DEBUG = True`
- **Admin:** Accede a `/admin/` con el superusuario para gestionar todo

---

## 📞 ¿Necesitas Ayuda?

Si encuentras problemas:

1. Revisa los logs en la consola
2. Verifica que MariaDB esté corriendo
3. Confirma que el venv esté activado
4. Revisa las credenciales en `settings.py`
5. Consulta `SETUP_DATABASE.md` para más detalles

---

**¡Listo! Ya deberías tener el proyecto funcionando en el PC del instituto. 🎉**

