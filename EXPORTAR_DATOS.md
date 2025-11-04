# 📤 Exportar Datos de MariaDB a Fixtures

## 🚀 Método Rápido (Recomendado)

### 1. Activar Entorno Virtual

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

### 2. Exportar Todos los Datos

```bash
python manage.py dumpdata tasks --indent 2 --natural-foreign --natural-primary --output tasks/fixtures/all_data.json
```

### 3. Exportar Modelos Específicos

```bash
# Usuarios y perfiles
python manage.py dumpdata auth.User tasks.PerfilUsuario --indent 2 --output tasks/fixtures/usuarios.json

# Catálogo de discos
python manage.py dumpdata tasks.Genero tasks.Artista tasks.Disco --indent 2 --output tasks/fixtures/catalogo_discos.json

# Instrumentos
python manage.py dumpdata tasks.CategoriaInstrumento tasks.Instrumento --indent 2 --output tasks/fixtures/instrumentos.json

# Inventario
python manage.py dumpdata tasks.Sucursal tasks.Inventario tasks.InventarioMovimiento --indent 2 --output tasks/fixtures/inventario.json
```

---

## 📝 Usar el Script Automático

Si prefieres usar el script `exportar_datos.py`:

```bash
# 1. Activar venv
.\venv\Scripts\Activate.ps1

# 2. Ejecutar script
python exportar_datos.py
```

Este script exporta todos los modelos a archivos JSON separados en `tasks/fixtures/`.

---

## 📋 Orden de Exportación (Importante para Cargar)

Si exportas por separado, exporta en este orden:

1. `auth.User` (usuarios base)
2. `tasks.PerfilUsuario` (perfiles)
3. `tasks.Genero` (géneros)
4. `tasks.Artista` (artistas)
5. `tasks.CategoriaInstrumento` (categorías de instrumentos)
6. `tasks.Sucursal` (sucursales)
7. `tasks.Disco` (discos)
8. `tasks.Instrumento` (instrumentos)
9. `tasks.Inventario` (inventario)
10. `tasks.InventarioMovimiento` (movimientos)

---

## 📥 Cargar Datos en Otra Base de Datos

```bash
# Activar venv
.\venv\Scripts\Activate.ps1

# Cargar todos los fixtures
python manage.py loaddata tasks/fixtures/all_data.json

# O cargar uno por uno en orden
python manage.py loaddata tasks/fixtures/genero.json
python manage.py loaddata tasks/fixtures/artista.json
python manage.py loaddata tasks/fixtures/disco.json
# ... etc
```

---

## ⚠️ Notas Importantes

- **Activa el venv** antes de ejecutar comandos Django
- Los fixtures JSON son solo para datos de ejemplo
- Las imágenes NO se incluyen en los fixtures (se guardan en `media/`)
- Para producción, usa backups SQL completos de MariaDB

---

## 🔧 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'MySQLdb'"
**Solución:** Activa el entorno virtual primero:
```bash
.\venv\Scripts\Activate.ps1
```

### Error: "No such file or directory"
**Solución:** Asegúrate de estar en el directorio raíz del proyecto:
```bash
cd "C:\Users\danie\Desktop\A Destiempo"
```

### Error: "Access denied for user"
**Solución:** Verifica las credenciales en `Destiempo/settings.py`

