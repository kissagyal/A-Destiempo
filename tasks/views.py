from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Disco, Instrumento, Genero, CategoriaInstrumento, PerfilUsuario
from .forms import SignUpForm

def es_empleado(user):
    if user.is_authenticated:
        try:
            perfil = user.perfilusuario
            return perfil.tipo_usuario == 'empleado'
        except PerfilUsuario.DoesNotExist:
            return False
    return False

def inicio(request):
    """Vista principal que muestra los productos destacados"""
    discos_destacados = Disco.objects.filter(activo=True)[:6]
    instrumentos_destacados = Instrumento.objects.filter(activo=True)[:6]
    
    context = {
        'discos_destacados': discos_destacados,
        'instrumentos_destacados': instrumentos_destacados,
    }
    return render(request, 'inicio.html', context)

def lista_discos(request):
    """Lista todos los discos disponibles con filtros"""
    discos = Disco.objects.filter(activo=True)
    generos = Genero.objects.all()
    formato_filter = request.GET.get('formato')
    genero_filter = request.GET.get('genero')
    search = request.GET.get('search')
    
    if formato_filter:
        discos = discos.filter(formato=formato_filter)
    if genero_filter:
        discos = discos.filter(genero_id=genero_filter)
    if search:
        discos = discos.filter(
            Q(titulo__icontains=search) | 
            Q(artista__nombre__icontains=search)
        )
    
    context = {
        'discos': discos,
        'generos': generos,
        'formato_actual': formato_filter,
        'genero_actual': genero_filter,
        'search_actual': search,
    }
    return render(request, 'discos/lista_discos.html', context)

def lista_instrumentos(request):
    """Lista todos los instrumentos disponibles con filtros"""
    instrumentos = Instrumento.objects.filter(activo=True)
    categorias = CategoriaInstrumento.objects.all()
    categoria_filter = request.GET.get('categoria')
    estado_filter = request.GET.get('estado')
    search = request.GET.get('search')
    
    if categoria_filter:
        instrumentos = instrumentos.filter(categoria_id=categoria_filter)
    if estado_filter:
        instrumentos = instrumentos.filter(estado=estado_filter)
    if search:
        instrumentos = instrumentos.filter(
            Q(nombre__icontains=search) | 
            Q(marca__icontains=search) |
            Q(modelo__icontains=search)
        )
    
    context = {
        'instrumentos': instrumentos,
        'categorias': categorias,
        'categoria_actual': categoria_filter,
        'estado_actual': estado_filter,
        'search_actual': search,
    }
    return render(request, 'instrumentos/lista_instrumentos.html', context)

def detalle_disco(request, disco_id):
    """Vista de detalle de un disco específico"""
    disco = get_object_or_404(Disco, id=disco_id, activo=True)
    
    # Discos relacionados del mismo artista
    discos_relacionados = Disco.objects.filter(
        artista=disco.artista,
        activo=True
    ).exclude(id=disco_id)[:4]
    
    context = {
        'disco': disco,
        'discos_relacionados': discos_relacionados,
    }
    return render(request, 'discos/detalle_disco.html', context)

def detalle_instrumento(request, instrumento_id):
    """Vista de detalle de un instrumento específico"""
    instrumento = get_object_or_404(Instrumento, id=instrumento_id, activo=True)
    
    # Instrumentos relacionados de la misma categoría
    instrumentos_relacionados = Instrumento.objects.filter(
        categoria=instrumento.categoria,
        activo=True
    ).exclude(id=instrumento_id)[:4]
    
    context = {
        'instrumento': instrumento,
        'instrumentos_relacionados': instrumentos_relacionados,
    }
    return render(request, 'instrumentos/detalle_instrumento.html', context)

@login_required
@user_passes_test(es_empleado)
def panel_empleado(request):
    """Panel de control para empleados"""
    discos_recientes = Disco.objects.all().order_by('-fecha_agregado')[:5]
    instrumentos_recientes = Instrumento.objects.all().order_by('-fecha_agregado')[:5]
    
    context = {
        'discos_recientes': discos_recientes,
        'instrumentos_recientes': instrumentos_recientes,
    }
    return render(request, 'empleado/panel.html', context)

def helloworld(request):
    """Vista de registro de usuarios"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Crear perfil de usuario
            PerfilUsuario.objects.create(user=user, tipo_usuario='usuario')
            messages.success(request, '¡Cuenta creada exitosamente!')
            return redirect('inicio')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})