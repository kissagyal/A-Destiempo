# 🎵 A Destiempo - E-commerce de Música e Instrumentos

E-commerce moderno para venta de discos de música e instrumentos musicales, desarrollado con Django 5.2.7 y MariaDB.

## 🚀 Características

- **Catálogo de Discos**: Búsqueda por género, artista, año y formato
- **Catálogo de Instrumentos**: Categorización por instrumentos, refacciones y accesorios
- **Sistema de Inventario**: Multi-sucursal con seguimiento de stock
- **Roles de Usuario**: Cliente y Vendedor con permisos diferenciados
- **Panel de Vendedor**: CRUD completo para gestión de productos
- **Carrito de Compras**: Sistema de compras para clientes registrados
- **Diseño Moderno**: Inspirado en Tidal y Fender

## 📋 Requisitos

- Python 3.13+
- MariaDB 10.x (o MySQL 8.x)
- pip (gestor de paquetes de Python)

## 🛠️ Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/a-destiempo.git
cd a-destiempo
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos

1. Crear base de datos en MariaDB:
```sql
CREATE DATABASE adestiempo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Configurar credenciales en `Destiempo/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'adestiempo',
        'USER': 'root',
        'PASSWORD': 'tu_password',
        'HOST': '127.0.0.1',
        'PORT': '3309',
        # ...
    }
}
```

### 5. Aplicar Migraciones

```bash
python manage.py migrate
```

### 6. Crear Superusuario

```bash
python manage.py createsuperuser
```

### 7. Cargar Datos de Ejemplo (Opcional)

```bash
python manage.py loaddata tasks/fixtures/*.json
```

### 8. Ejecutar Servidor

```bash
python manage.py runserver
```

Visita `http://127.0.0.1:8000/`

## 📁 Estructura del Proyecto

```
A Destiempo/
├── Destiempo/          # Configuración del proyecto
│   ├── settings.py     # Configuración principal
│   ├── urls.py        # URLs del proyecto
│   └── ...
├── tasks/              # Aplicación principal
│   ├── models.py      # Modelos de datos
│   ├── views.py       # Vistas
│   ├── admin.py       # Configuración del admin
│   ├── forms.py       # Formularios
│   ├── fixtures/      # Datos de ejemplo (JSON)
│   └── templates/     # Plantillas HTML
├── static/            # Archivos estáticos (CSS, JS)
├── media/             # Archivos subidos (imágenes)
├── requirements.txt   # Dependencias Python
└── manage.py          # Script de gestión Django
```

## 👥 Usuarios y Permisos

### Tipos de Usuario

- **Visitante**: Puede ver catálogo, requiere login para comprar
- **Cliente**: Puede comprar, ver carrito, hacer checkout
- **Vendedor**: Todo lo del cliente + panel de administración, CRUDs de productos

### Credenciales de Prueba

Si cargas los fixtures, tendrás:
- **Cliente**: `cliente1` / `cliente123`
- **Vendedor**: `vendedor1` / `vendedor123`

## 🔐 Permisos y Seguridad

- Rutas protegidas con decoradores (`@login_required_with_message`, `@empleado_required`)
- Mensajes de error personalizados
- Redirecciones según tipo de usuario
- Ver `RESUMEN_PERMISOS.md` para detalles completos

## 📊 Base de Datos

- **Motor**: MariaDB/MySQL
- **Migraciones**: Django ORM
- **Fixtures**: Datos de ejemplo en `tasks/fixtures/`

Ver `SETUP_DATABASE.md` para guía completa de configuración y backup.

## 🎨 Diseño

- Bootstrap 5.3
- Font Awesome 6.4
- Diseño oscuro moderno
- Responsive
- Logo integrado en navbar y hero

## 📦 Exportar/Importar Datos

### Exportar Datos Actuales

```bash
python exportar_datos.py
```

Esto crea fixtures JSON en `tasks/fixtures/` para cada modelo.

### Importar Datos

```bash
python manage.py loaddata tasks/fixtures/*.json
```

## 🧪 Testing

Para probar los CRUDs y permisos:

1. **Como Visitante**: Intenta agregar al carrito → verás mensaje de login
2. **Como Cliente**: Puedes agregar al carrito, pero no acceder al panel
3. **Como Vendedor**: Acceso completo al panel y CRUDs

## 📝 Comandos Útiles

```bash
# Aplicar migraciones
python manage.py migrate

# Crear nuevas migraciones
python manage.py makemigrations

# Exportar datos
python exportar_datos.py

# Cargar datos
python manage.py loaddata tasks/fixtures/*.json

# Crear superusuario
python manage.py createsuperuser

# Shell de Django
python manage.py shell
```

## 🐛 Solución de Problemas

### Error de conexión a MariaDB
- Verifica que MariaDB esté corriendo
- Revisa credenciales en `settings.py`
- Confirma que la base de datos existe

### Error de migraciones
```bash
python manage.py migrate --run-syncdb
```

### Error de permisos
- Verifica que el usuario de MariaDB tenga permisos
- Revisa `RESUMEN_PERMISOS.md`

## 📄 Licencia

Este proyecto es privado.

## 👤 Autor

Desarrollado para A Destiempo

---

Para más detalles sobre la base de datos, ver `SETUP_DATABASE.md`
Para más detalles sobre permisos, ver `RESUMEN_PERMISOS.md`

