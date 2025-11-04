# ✅ Checklist de Instalación - PC del Instituto

Usa este checklist para asegurarte de que todo esté configurado correctamente.

---

## 📦 Preparación

- [ ] Python 3.13+ instalado (`python --version`)
- [ ] MariaDB instalado y corriendo
- [ ] Git instalado (opcional, para clonar)
- [ ] Proyecto descargado/clonado

---

## 🔧 Configuración del Proyecto

- [ ] Entorno virtual creado (`python -m venv venv`)
- [ ] Entorno virtual activado (verás `(venv)` en la consola)
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
  - [ ] Django instalado
  - [ ] mysqlclient instalado
  - [ ] Pillow instalado

---

## 🗄️ Base de Datos

- [ ] MariaDB corriendo
- [ ] Base de datos `adestiempo` creada
- [ ] Credenciales anotadas (usuario, password, puerto)
- [ ] `Destiempo/settings.py` configurado con credenciales correctas
  - [ ] `NAME`: 'adestiempo'
  - [ ] `USER`: (tu usuario MariaDB)
  - [ ] `PASSWORD`: (tu password MariaDB)
  - [ ] `PORT`: (tu puerto, ej: 3306)

---

## 🚀 Django

- [ ] Configuración verificada (`python manage.py check`)
- [ ] Migraciones aplicadas (`python manage.py migrate`)
- [ ] Tablas creadas en la base de datos (verificar en MariaDB)
- [ ] Superusuario creado (`python manage.py createsuperuser`)
- [ ] Credenciales del superusuario anotadas

---

## 📥 Datos de Ejemplo (Opcional)

- [ ] Fixtures cargados (`python manage.py loaddata tasks/fixtures/all_data.json`)
- [ ] Datos visibles en el admin (`/admin/`)
- [ ] Productos de ejemplo en la página principal

---

## 🧪 Pruebas

- [ ] Servidor corriendo (`python manage.py runserver`)
- [ ] Página principal accesible (`http://127.0.0.1:8000/`)
- [ ] Admin accesible (`http://127.0.0.1:8000/admin/`)
- [ ] Login funcionando (como cliente)
- [ ] Login funcionando (como vendedor)
- [ ] Panel de vendedor accesible (`/panel-empleado/`)
- [ ] CRUDs funcionando (crear/editar/eliminar productos)

---

## 🔐 Credenciales Registradas

Guarda estas credenciales en un lugar seguro:

**Superusuario:**
- Username: _______________
- Password: _______________

**MariaDB:**
- Usuario: _______________
- Password: _______________
- Puerto: _______________

**Credenciales de Prueba (si cargaste fixtures):**
- Cliente: `cliente1` / `cliente123`
- Vendedor: `vendedor1` / `vendedor123`

---

## ✅ Verificación Final

- [ ] Todo funciona correctamente
- [ ] Puedo acceder como cliente
- [ ] Puedo acceder como vendedor
- [ ] Puedo gestionar productos desde el panel
- [ ] Los permisos funcionan correctamente

---

## 📝 Notas Adicionales

Escribe aquí cualquier nota o problema encontrado:

_____________________________________________________________
_____________________________________________________________
_____________________________________________________________

---

**Fecha de instalación:** _______________

**Instalado por:** _______________

