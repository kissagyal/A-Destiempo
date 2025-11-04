#!/bin/bash

echo "═══════════════════════════════════════════════════════════════"
echo "  SUBIENDO PROYECTO A GITHUB"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# 1. Agregar .gitignore primero
echo "[1/5] Agregando .gitignore actualizado..."
git add .gitignore

# 2. Agregar documentación
echo "[2/5] Agregando documentación..."
git add README.md SETUP_DATABASE.md GUIA_INSTALACION_INSTITUTO.md
git add EXPORTAR_DATOS.md RESUMEN_PERMISOS.md CHECKLIST_INSTITUTO.md
git add INSTRUCCIONES_RAPIDAS.txt COMANDOS_GIT.txt

# 3. Agregar archivos de configuración
echo "[3/5] Agregando archivos de configuración..."
git add requirements.txt exportar_datos.py

# 4. Agregar código del proyecto
echo "[4/5] Agregando código del proyecto..."
git add Destiempo/ tasks/ static/ manage.py

# 5. Hacer commit
echo "[5/5] Haciendo commit..."
git commit -m "feat: Proyecto completo A Destiempo - E-commerce de música e instrumentos

- Sistema de inventario multi-sucursal
- Roles de usuario (Cliente/Vendedor)
- CRUDs completos para vendedores
- Panel de administración
- Catálogo de discos e instrumentos
- Sistema de carrito y checkout
- Fixtures de datos de ejemplo
- Documentación completa
- Migraciones de base de datos
- Diseño moderno inspirado en Tidal/Fender"

# 6. Subir a GitHub
echo ""
echo "Subiendo a GitHub..."
git push origin main

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ¡PROYECTO SUBIDO EXITOSAMENTE!"
echo "═══════════════════════════════════════════════════════════════"

