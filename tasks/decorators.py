from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from functools import wraps


def login_required_with_message(view_func):
    """
    Decorador que requiere autenticación y muestra mensaje específico
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "¡Espera, debes iniciar sesión antes!")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def empleado_required(view_func):
    """
    Decorador que requiere rol de vendedor
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "¡Espera, debes iniciar sesión antes!")
            return redirect('login')
        
        try:
            perfil = request.user.perfilusuario
            if perfil.tipo_usuario != 'vendedor':
                messages.error(request, "No tienes permisos para acceder a esta sección. Solo los vendedores pueden acceder.")
                return redirect('inicio')
        except:
            messages.error(request, "No tienes permisos para acceder a esta sección. Solo los vendedores pueden acceder.")
            return redirect('inicio')
        
        return view_func(request, *args, **kwargs)
    return wrapper
