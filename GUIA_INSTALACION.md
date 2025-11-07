# Guía de Instalación - A Destiempo

Esta guía te ayudará a instalar y configurar el proyecto "A Destiempo" en un nuevo PC.

## Requisitos Previos

1. **Python 3.10 o superior**
2. **MariaDB 10.6 o superior** (o MySQL 8.0+)
3. **Git** (para clonar el repositorio)
4. **pip** (gestor de paquetes de Python)

## Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/kissagyal/A-Destiempo.git
cd A-Destiempo
```

## Paso 2: Crear Entorno Virtual

```bash
# Windows
python -m venv venv

# Activar el entorno virtual
# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat
```

## Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

## Paso 4: Configurar MariaDB/MySQL

1. **Crear la base de datos:**
   ```sql
   CREATE DATABASE adestiempo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. **Crear un usuario (opcional, puedes usar root):**
   ```sql
   CREATE USER 'adestiempo_user'@'localhost' IDENTIFIED BY 'tu_contraseña';
   GRANT ALL PRIVILEGES ON adestiempo.* TO 'adestiempo_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

## Paso 5: Configurar el Proyecto

1. **Editar `Destiempo/settings.py`** con tus credenciales de base de datos:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'adestiempo',
           'USER': 'root',  # o tu_usuario
           'PASSWORD': '',  # tu_contraseña
           'HOST': '127.0.0.1',
           'PORT': '3309',  # o 3306 si es el puerto por defecto
           'OPTIONS': {
               'charset': 'utf8mb4',
               'use_unicode': True,
           },
           'CONN_MAX_AGE': 60,
       }
   }
   ```

## Paso 6: Restaurar la Base de Datos

1. **Importar el backup de la base de datos:**
   ```bash
   mysql -u root -h 127.0.0.1 -P 3309 adestiempo < backup_adestiempo_20251106_233030.sql
   ```

   O si usas un usuario diferente:
   ```bash
   mysql -u adestiempo_user -p -h 127.0.0.1 -P 3309 adestiempo < backup_adestiempo_20251106_233030.sql
   ```

## Paso 7: Restaurar las Imágenes

1. **Extraer el backup de imágenes:**
   ```bash
   # Windows PowerShell
   Expand-Archive -Path backup_media_20251106_233052.zip -DestinationPath . -Force
   ```

   O manualmente:
   - Descomprimir `backup_media_20251106_233052.zip`
   - Copiar el contenido de la carpeta `media` extraída a la raíz del proyecto

## Paso 8: Ejecutar Migraciones (si es necesario)

```bash
python manage.py migrate
```

## Paso 9: Crear Superusuario (opcional)

```bash
python manage.py createsuperuser
```

## Paso 10: Recopilar Archivos Estáticos

```bash
python manage.py collectstatic --noinput
```

## Paso 11: Ejecutar el Servidor

```bash
python manage.py runserver
```

El proyecto estará disponible en: `http://127.0.0.1:8000`

## Usuarios de Prueba

### Cliente:
- **Usuario:** cliente1
- **Contraseña:** (verificar en la base de datos o crear uno nuevo)

### Vendedor:
- **Usuario:** vendedor1
- **Contraseña:** (verificar en la base de datos o crear uno nuevo)

## Solución de Problemas

### Error de conexión a la base de datos:
- Verifica que MariaDB/MySQL esté corriendo
- Verifica las credenciales en `settings.py`
- Verifica el puerto (3306 o 3309)

### Error al importar la base de datos:
- Asegúrate de que la base de datos esté creada
- Verifica que el usuario tenga permisos
- En MariaDB 12.0, usa: `mysql -u root -h 127.0.0.1 -P 3309 adestiempo < backup_adestiempo_20251106_233030.sql`

### Las imágenes no se muestran:
- Verifica que el directorio `media/` exista en la raíz del proyecto
- Verifica que `MEDIA_URL` y `MEDIA_ROOT` estén configurados en `settings.py`
- En desarrollo, las imágenes se sirven automáticamente si `DEBUG = True`

### Error de migraciones:
- Ejecuta: `python manage.py makemigrations`
- Luego: `python manage.py migrate`

## Estructura de Directorios Importante

```
A-Destiempo/
├── media/              # Imágenes de productos (debe existir)
│   ├── discos/
│   ├── instrumentos/
│   └── refacciones/
├── static/             # Archivos estáticos (CSS, JS)
├── tasks/              # Aplicación principal
│   ├── migrations/     # Migraciones de base de datos
│   ├── templates/      # Templates HTML
│   └── ...
├── Destiempo/          # Configuración del proyecto
├── manage.py
├── requirements.txt
└── backup_adestiempo_*.sql  # Backup de base de datos
```

## Notas Importantes

1. **No subir credenciales a Git**: El archivo `.gitignore` excluye archivos sensibles
2. **Backups**: Los backups de base de datos e imágenes están en el repositorio
3. **Media files**: El directorio `media/` no se sube a Git, pero el backup en zip sí
4. **Puerto de MariaDB**: Por defecto es 3306, pero este proyecto usa 3309

## Comandos Útiles

```bash
# Ver estado de Git
git status

# Ver logs de commits
git log

# Actualizar desde el repositorio
git pull origin main

# Verificar que todo esté instalado
pip list

# Verificar conexión a la base de datos
python manage.py dbshell
```

