# Comandos Git para Subir Cambios

## Pasos para Subir al Repositorio

### 1. Ver el estado actual
```bash
git status
```

### 2. Agregar todos los archivos modificados
```bash
git add .
```

O si quieres agregar archivos específicos:
```bash
git add tasks/
git add Destiempo/
git add static/
git add requirements.txt
git add .gitignore
```

### 3. Hacer commit (guardar cambios)
```bash
git commit -m "Mejoras: CRUD de discos, búsqueda de metadatos, stock por formato, validaciones de imagen"
```

### 4. Conectar con el repositorio remoto (si aún no lo has hecho)
```bash
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
```

O si ya está conectado, verificar:
```bash
git remote -v
```

### 5. Subir cambios al repositorio remoto
```bash
git push -u origin main
```

O si tu rama se llama `master`:
```bash
git push -u origin master
```

---

## Comandos Rápidos (Todo en uno)

Si ya tienes el repositorio remoto configurado:

```bash
git add .
git commit -m "Mejoras: CRUD de discos, búsqueda de metadatos, stock por formato, validaciones de imagen"
git push
```

---

## Si es la primera vez

1. **Crear repositorio en GitHub** (si no existe)
2. **Conectar:**
   ```bash
   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   ```
3. **Agregar y commit:**
   ```bash
   git add .
   git commit -m "Primer commit: Proyecto A Destiempo"
   ```
4. **Subir:**
   ```bash
   git branch -M main
   git push -u origin main
   ```

---

## Verificar antes de subir

```bash
# Ver qué archivos se van a subir
git status

# Ver los cambios específicos
git diff

# Ver el historial de commits
git log --oneline
```

