from .models import PerfilUsuario

def user_profile(request):
    """
    Context processor que agrega el perfil del usuario al contexto
    """
    if request.user.is_authenticated:
        try:
            user_profile = PerfilUsuario.objects.get(user=request.user)
            return {'user_profile': user_profile}
        except PerfilUsuario.DoesNotExist:
            return {'user_profile': None}
    return {'user_profile': None}
