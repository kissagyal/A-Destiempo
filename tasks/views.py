from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from .models import Disco, Instrumento, Genero, CategoriaInstrumento, PerfilUsuario, Sucursal, Inventario, Artista
from .forms import SignUpForm, DiscoForm, InstrumentoForm
from .decorators import login_required_with_message, empleado_required

def es_empleado(user):
    if user.is_authenticated:
        try:
            perfil = user.perfilusuario
            return perfil.tipo_usuario == 'vendedor'
        except PerfilUsuario.DoesNotExist:
            return False
    return False

@csrf_protect
@never_cache
def login_view(request):
    """Vista personalizada de login que redirige según el tipo de usuario"""
    if request.user.is_authenticated:
        # Si ya está logueado, redirigir según su tipo
        try:
            perfil = request.user.perfilusuario
            if perfil.tipo_usuario == 'vendedor':
                return redirect('panel_empleado')
        except PerfilUsuario.DoesNotExist:
            pass
        return redirect('/')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            
            # Redirigir según el tipo de usuario
            try:
                perfil = user.perfilusuario
                if perfil.tipo_usuario == 'vendedor':
                    return redirect('panel_empleado')
            except PerfilUsuario.DoesNotExist:
                pass
            
            # Por defecto, redirigir a la página principal
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

def inicio(request):
    """Vista principal que muestra los productos destacados (para todos)"""
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
    artistas = Artista.objects.all()
    years = Disco.objects.values_list('año_lanzamiento', flat=True).distinct().order_by('-año_lanzamiento')
    formato_filter = request.GET.get('formato')
    genero_filter = request.GET.get('genero')
    artista_filter = request.GET.get('artista')
    year_filter = request.GET.get('year')
    search = request.GET.get('search')
    
    if formato_filter:
        discos = discos.filter(formato=formato_filter)
    if genero_filter:
        discos = discos.filter(genero_id=genero_filter)
    if artista_filter:
        discos = discos.filter(artista_id=artista_filter)
    if year_filter:
        discos = discos.filter(año_lanzamiento=year_filter)
    if search:
        discos = discos.filter(
            Q(titulo__icontains=search) | 
            Q(artista__nombre__icontains=search)
        )
    
    context = {
        'discos': discos,
        'generos': generos,
        'artistas': artistas,
        'years': years,
        'formato_actual': formato_filter,
        'genero_actual': genero_filter,
        'artista_actual': artista_filter,
        'year_actual': year_filter,
        'search_actual': search,
    }
    return render(request, 'discos/lista_discos.html', context)

def lista_instrumentos(request):
    """Lista todos los instrumentos disponibles con filtros"""
    instrumentos = Instrumento.objects.filter(activo=True)
    tipo_filter = request.GET.get('tipo')
    categorias = CategoriaInstrumento.objects.all()
    categoria_filter = request.GET.get('categoria')
    estado_filter = request.GET.get('estado')
    search = request.GET.get('search')
    
    # Filtro por tipo alto nivel (instrumento / refaccion / accesorio)
    if tipo_filter in ('instrumento', 'refaccion', 'accesorio'):
        instrumentos = instrumentos.filter(categoria__tipo=tipo_filter)
        categorias = categorias.filter(tipo=tipo_filter)
    
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
        'tipo_actual': tipo_filter,
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

@empleado_required
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
            PerfilUsuario.objects.create(user=user, tipo_usuario='cliente')
            messages.success(request, '¡Cuenta creada exitosamente!')
            return redirect('inicio')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})

# ===========================================
# VISTAS DE CARRITO Y COMPRA
# ===========================================

@login_required_with_message
def agregar_al_carrito_disco(request, disco_id):
    """Agregar disco al carrito (requiere autenticación)"""
    disco = get_object_or_404(Disco, id=disco_id, activo=True)
    
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        
        if not disco.tiene_stock():
            messages.error(request, f"El disco '{disco.titulo}' no tiene stock disponible.")
            return redirect('detalle_disco', disco_id=disco_id)
        
        # Aquí implementarías la lógica del carrito
        # Por ahora solo mostramos un mensaje de éxito
        messages.success(request, f"¡{disco.titulo} agregado al carrito!")
        return redirect('detalle_disco', disco_id=disco_id)
    
    return redirect('detalle_disco', disco_id=disco_id)

@login_required_with_message
def agregar_al_carrito_instrumento(request, instrumento_id):
    """Agregar instrumento al carrito (requiere autenticación)"""
    instrumento = get_object_or_404(Instrumento, id=instrumento_id, activo=True)
    
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        
        if not instrumento.tiene_stock():
            messages.error(request, f"El instrumento '{instrumento.nombre}' no tiene stock disponible.")
            return redirect('detalle_instrumento', instrumento_id=instrumento_id)
        
        # Aquí implementarías la lógica del carrito
        # Por ahora solo mostramos un mensaje de éxito
        messages.success(request, f"¡{instrumento.nombre} agregado al carrito!")
        return redirect('detalle_instrumento', instrumento_id=instrumento_id)
    
    return redirect('detalle_instrumento', instrumento_id=instrumento_id)

@login_required_with_message
def ver_carrito(request):
    """Ver carrito de compras (requiere autenticación)"""
    # Aquí implementarías la vista del carrito
    context = {
        'titulo': 'Mi Carrito',
        'items': [],  # Lista de items del carrito
    }
    return render(request, 'carrito/carrito.html', context)

@login_required_with_message
def checkout(request):
    """Proceso de checkout (requiere autenticación)"""
    # Aquí implementarías el proceso de checkout
    context = {
        'titulo': 'Finalizar Compra',
    }
    return render(request, 'carrito/checkout.html', context)

# ===========================================
# VISTAS CRUD PARA VENDEDOR
# ===========================================

@empleado_required
def crear_disco(request):
    """Crear nuevo disco"""
    if request.method == 'POST':
        form = DiscoForm(request.POST, request.FILES)
        if form.is_valid():
            disco = form.save()
            messages.success(request, f'¡Disco "{disco.titulo}" creado exitosamente!')
            return redirect('panel_empleado')
    else:
        form = DiscoForm()
    
    return render(request, 'empleado/disco_form.html', {'form': form, 'titulo': 'Crear Disco'})

@empleado_required
def editar_disco(request, disco_id):
    """Editar disco existente"""
    disco = get_object_or_404(Disco, id=disco_id)
    
    if request.method == 'POST':
        form = DiscoForm(request.POST, request.FILES, instance=disco)
        if form.is_valid():
            disco = form.save()
            messages.success(request, f'¡Disco "{disco.titulo}" actualizado exitosamente!')
            return redirect('panel_empleado')
    else:
        form = DiscoForm(instance=disco)
    
    return render(request, 'empleado/disco_form.html', {'form': form, 'disco': disco, 'titulo': 'Editar Disco'})

@empleado_required
def eliminar_disco(request, disco_id):
    """Eliminar disco"""
    disco = get_object_or_404(Disco, id=disco_id)
    
    if request.method == 'POST':
        titulo = disco.titulo
        disco.delete()
        messages.success(request, f'¡Disco "{titulo}" eliminado exitosamente!')
        return redirect('panel_empleado')
    
    return render(request, 'empleado/confirmar_eliminar.html', {'objeto': disco, 'tipo': 'disco'})

@empleado_required
def crear_instrumento(request):
    """Crear nuevo instrumento"""
    if request.method == 'POST':
        form = InstrumentoForm(request.POST, request.FILES)
        if form.is_valid():
            instrumento = form.save()
            messages.success(request, f'¡Instrumento "{instrumento.nombre}" creado exitosamente!')
            return redirect('panel_empleado')
    else:
        form = InstrumentoForm()
    
    return render(request, 'empleado/instrumento_form.html', {'form': form, 'titulo': 'Crear Instrumento'})

@empleado_required
def editar_instrumento(request, instrumento_id):
    """Editar instrumento existente"""
    instrumento = get_object_or_404(Instrumento, id=instrumento_id)
    
    if request.method == 'POST':
        form = InstrumentoForm(request.POST, request.FILES, instance=instrumento)
        if form.is_valid():
            instrumento = form.save()
            messages.success(request, f'¡Instrumento "{instrumento.nombre}" actualizado exitosamente!')
            return redirect('panel_empleado')
    else:
        form = InstrumentoForm(instance=instrumento)
    
    return render(request, 'empleado/instrumento_form.html', {'form': form, 'instrumento': instrumento, 'titulo': 'Editar Instrumento'})

@empleado_required
def eliminar_instrumento(request, instrumento_id):
    """Eliminar instrumento"""
    instrumento = get_object_or_404(Instrumento, id=instrumento_id)
    
    if request.method == 'POST':
        nombre = instrumento.nombre
        instrumento.delete()
        messages.success(request, f'¡Instrumento "{nombre}" eliminado exitosamente!')
        return redirect('panel_empleado')
    
    return render(request, 'empleado/confirmar_eliminar.html', {'objeto': instrumento, 'tipo': 'instrumento'})