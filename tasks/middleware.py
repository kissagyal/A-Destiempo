"""
Middleware para limpiar sesiones inválidas y verificar autenticación
"""
from django.contrib.auth import logout
from django.contrib.auth.models import AnonymousUser

class SessionCleanupMiddleware:
    """
    Middleware para limpiar sesiones inválidas o expiradas
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar si el usuario está autenticado pero la sesión es inválida
        if request.user.is_authenticated:
            # Verificar que el usuario existe en la base de datos
            try:
                # Forzar la verificación del usuario
                request.user.refresh_from_db()
            except Exception:
                # Si hay error, el usuario no existe, cerrar sesión
                logout(request)
        
        response = self.get_response(request)
        return response

