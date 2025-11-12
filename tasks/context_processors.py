from django.conf import settings
from .models import PerfilUsuario

def user_profile(request):
    """
    Context processor que agrega el perfil del usuario al contexto
    """
    context = {}
    
    if request.user.is_authenticated:
        try:
            user_profile = PerfilUsuario.objects.get(user=request.user)
            context['user_profile'] = user_profile
        except PerfilUsuario.DoesNotExist:
            context['user_profile'] = None
    else:
        context['user_profile'] = None
    
    return context
