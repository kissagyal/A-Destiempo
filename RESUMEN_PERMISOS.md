# Resumen de Permisos - A Destiempo

## Tipos de Usuario

### 1. Visitante (No autenticado)
**Acceso:**
- ✅ Ver página principal (productos destacados)
- ✅ Ver catálogo de discos
- ✅ Ver catálogo de instrumentos
- ✅ Ver detalles de discos
- ✅ Ver detalles de instrumentos
- ✅ Registrarse (signup)

**Restricciones:**
- ❌ No puede agregar productos al carrito
- ❌ No puede acceder al carrito
- ❌ No puede hacer checkout
- ❌ No puede acceder al panel de vendedor
- ❌ No puede hacer CRUDs de productos

**Mensajes:**
- Si intenta agregar al carrito: "¡Espera, debes iniciar sesión antes!"
- Redirige a: `/accounts/login/`

---

### 2. Cliente (Usuario registrado con tipo 'cliente')
**Acceso:**
- ✅ Ver página principal (productos destacados)
- ✅ Ver catálogo de discos
- ✅ Ver catálogo de instrumentos
- ✅ Ver detalles de discos
- ✅ Ver detalles de instrumentos
- ✅ Agregar productos al carrito
- ✅ Ver carrito
- ✅ Hacer checkout

**Restricciones:**
- ❌ No puede acceder al panel de vendedor
- ❌ No puede hacer CRUDs de productos
- ❌ No puede acceder al admin de Django

**Mensajes:**
- Si intenta acceder al panel: "No tienes permisos para acceder a esta sección. Solo los vendedores pueden acceder."
- Redirige a: `/` (página principal)

---

### 3. Vendedor (Usuario con tipo 'vendedor')
**Acceso:**
- ✅ Todo lo que puede hacer un Cliente
- ✅ Acceder al panel de empleado (`/panel-empleado/`)
- ✅ Crear discos (`/panel-empleado/disco/crear/`)
- ✅ Editar discos (`/panel-empleado/disco/<id>/editar/`)
- ✅ Eliminar discos (`/panel-empleado/disco/<id>/eliminar/`)
- ✅ Crear instrumentos (`/panel-empleado/instrumento/crear/`)
- ✅ Editar instrumentos (`/panel-empleado/instrumento/<id>/editar/`)
- ✅ Eliminar instrumentos (`/panel-empleado/instrumento/<id>/eliminar/`)
- ✅ Acceder al admin de Django (`/admin/`)

**Permisos:**
- `is_staff = True` (automático por señal)
- Permisos completos en el admin de Django

**Redirecciones:**
- Después de login: `/panel-empleado/`
- Clientes después de login: `/` (página principal)

---

## Decoradores de Seguridad

### `@login_required_with_message`
- **Uso:** Protege vistas que requieren autenticación (carrito, checkout)
- **Acción:** Si no está autenticado, muestra mensaje y redirige a login
- **Mensaje:** "¡Espera, debes iniciar sesión antes!"

### `@empleado_required`
- **Uso:** Protege vistas del panel de vendedor
- **Acción:** Si no está autenticado o no es vendedor, muestra mensaje y redirige
- **Mensajes:**
  - No autenticado: "¡Espera, debes iniciar sesión antes!"
  - No es vendedor: "No tienes permisos para acceder a esta sección. Solo los vendedores pueden acceder."

---

## URLs Protegidas

### Requieren Autenticación (Cliente o Vendedor):
- `/carrito/` - Ver carrito
- `/checkout/` - Checkout
- `/disco/<id>/agregar/` - Agregar disco al carrito
- `/instrumento/<id>/agregar/` - Agregar instrumento al carrito

### Requieren Rol de Vendedor:
- `/panel-empleado/` - Panel principal
- `/panel-empleado/disco/crear/` - Crear disco
- `/panel-empleado/disco/<id>/editar/` - Editar disco
- `/panel-empleado/disco/<id>/eliminar/` - Eliminar disco
- `/panel-empleado/instrumento/crear/` - Crear instrumento
- `/panel-empleado/instrumento/<id>/editar/` - Editar instrumento
- `/panel-empleado/instrumento/<id>/eliminar/` - Eliminar instrumento

---

## Credenciales de Prueba

### Cliente:
- **Username:** `cliente1`
- **Password:** `cliente123`
- **Tipo:** `cliente`

### Vendedor:
- **Username:** `vendedor1`
- **Password:** `vendedor123`
- **Tipo:** `vendedor`
- **Staff:** `True`

---

## Funcionalidades por Tipo de Usuario

| Funcionalidad | Visitante | Cliente | Vendedor |
|--------------|-----------|---------|----------|
| Ver catálogo | ✅ | ✅ | ✅ |
| Ver detalles | ✅ | ✅ | ✅ |
| Agregar al carrito | ❌ | ✅ | ✅ |
| Ver carrito | ❌ | ✅ | ✅ |
| Checkout | ❌ | ✅ | ✅ |
| Panel vendedor | ❌ | ❌ | ✅ |
| Crear productos | ❌ | ❌ | ✅ |
| Editar productos | ❌ | ❌ | ✅ |
| Eliminar productos | ❌ | ❌ | ✅ |
| Admin Django | ❌ | ❌ | ✅ |

