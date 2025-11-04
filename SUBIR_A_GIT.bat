@echo off
echo ========================================
echo   SUBIENDO PROYECTO A GITHUB
echo ========================================
echo.

echo [1/4] Agregando .gitignore actualizado...
git add .gitignore

echo [2/4] Agregando todos los archivos nuevos...
git add .

echo [3/4] Haciendo commit...
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

echo [4/4] Subiendo a GitHub...
git push origin main

echo.
echo ========================================
echo   ¡PROYECTO SUBIDO EXITOSAMENTE!
echo ========================================
pause

