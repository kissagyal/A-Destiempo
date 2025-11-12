from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Sum, Count
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
import random
from decimal import Decimal
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from .models import (Disco, Instrumento, Genero, CategoriaInstrumento, PerfilUsuario, Sucursal,
                     Inventario, Artista, Favorito, Refaccion, CategoriaRefaccion, Pedido,
                     ItemPedido, HeroBanner)
from .forms import SignUpForm, DiscoForm, InstrumentoForm, RefaccionForm, HeroBannerForm
from .decorators import login_required_with_message, empleado_required
from .metadata_service import buscar_metadatos_disco, descargar_portada
from .chat_bot import ChatBot


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
            
            try:
                perfil = user.perfilusuario
                if perfil.tipo_usuario == 'vendedor':
                    return redirect('panel_empleado')
            except PerfilUsuario.DoesNotExist:
                pass
            
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

def _seleccionar_artista_destacado(request, force_id=None):
    """
    Devuelve un artista aleatorio que tenga al menos un disco activo.
    Intenta evitar repetir el mismo artista consecutivamente para el mismo visitante.
    """
    artistas_qs = Artista.objects.filter(discos__activo=True).distinct()
    artistas_ids = list(artistas_qs.values_list('id', flat=True))
    
    if not artistas_ids:
        return None
    
    if force_id and force_id in artistas_ids:
        request.session['ultimo_artista_destacado'] = force_id
        return artistas_qs.get(id=force_id)
    
    ultimo_id = request.session.get('ultimo_artista_destacado')
    candidatos = artistas_ids.copy()
    if ultimo_id in candidatos and len(candidatos) > 1:
        candidatos = [aid for aid in candidatos if aid != ultimo_id]
    
    artista_id = random.choice(candidatos)
    request.session['ultimo_artista_destacado'] = artista_id
    return artistas_qs.get(id=artista_id)


def inicio(request):
    """Vista principal que muestra los productos destacados (para todos)"""
    # Verificar autenticación válida
    if request.user.is_authenticated:
        try:
            # Verificar que el usuario existe y tiene perfil
            request.user.refresh_from_db()
            perfil = getattr(request.user, 'perfilusuario', None)
            if not perfil:
                # Si no tiene perfil, cerrar sesión
                from django.contrib.auth import logout
                logout(request)
        except Exception:
            # Si hay error, cerrar sesión
            from django.contrib.auth import logout
            logout(request)
    
    # Seleccionar artista destacado aleatorio
    artista_hero = _seleccionar_artista_destacado(request)
    disco_destacado = None
    hero_banner_config = {
        'title': 'A Destiempo',
        'subtitle': 'Descubre la mejor colección de discos, vinilos e instrumentos musicales. Donde la música cobra vida.',
        'button1_text': 'Explorar Discos',
        'button1_url': reverse('lista_discos'),
        'button2_text': 'Ver Instrumentos',
        'button2_url': reverse('lista_instrumentos'),
        'background_url': None,
    }
    banner_personalizado = None
    
    if artista_hero:
        banner_personalizado = getattr(artista_hero, 'hero_banner', None)

        if banner_personalizado:
            hero_banner_config['title'] = banner_personalizado.titulo or hero_banner_config['title']
            hero_banner_config['subtitle'] = banner_personalizado.subtitulo or hero_banner_config['subtitle']
            hero_banner_config['button1_text'] = banner_personalizado.boton_1_texto or hero_banner_config['button1_text']
            hero_banner_config['button1_url'] = banner_personalizado.get_boton_1_url()
            hero_banner_config['button2_text'] = banner_personalizado.boton_2_texto or hero_banner_config['button2_text']
            hero_banner_config['button2_url'] = banner_personalizado.get_boton_2_url()
            if banner_personalizado.imagen:
                hero_banner_config['background_url'] = banner_personalizado.imagen.url

        if not hero_banner_config['background_url'] and artista_hero.foto:
            hero_banner_config['background_url'] = artista_hero.foto.url
        
        # Obtener un disco destacado del artista para mostrar en el hero
        discos_del_artista = (
            Disco.objects.filter(
                artista=artista_hero,
                activo=True
            )
            .exclude(portada__isnull=True)
            .exclude(portada='')
        )
        
        if discos_del_artista.exists():
            disco_destacado = random.choice(list(discos_del_artista))
    
    # Obtener discos destacados (solo activos y con stock o disponibles)
    discos_destacados = Disco.objects.filter(activo=True).order_by('-fecha_agregado')[:6]
    instrumentos_destacados = Instrumento.objects.filter(activo=True).order_by('-fecha_agregado')[:6]

    context = {
        'artista_hero': artista_hero,
        'disco_destacado': disco_destacado,
        'discos_destacados': discos_destacados,
        'instrumentos_destacados': instrumentos_destacados,
        'hero_banner_config': hero_banner_config,
        'hero_banner_personalizado': banner_personalizado,
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
    
    # Verificar si está en favoritos
    es_favorito = False
    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(usuario=request.user, disco=disco).exists()
    
    context = {
        'disco': disco,
        'discos_relacionados': discos_relacionados,
        'es_favorito': es_favorito,
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
    
    # Verificar si está en favoritos
    es_favorito = False
    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(usuario=request.user, instrumento=instrumento).exists()
    
    context = {
        'instrumento': instrumento,
        'instrumentos_relacionados': instrumentos_relacionados,
        'es_favorito': es_favorito,
    }
    return render(request, 'instrumentos/detalle_instrumento.html', context)

def lista_refacciones(request):
    """Lista todas las refacciones disponibles con filtros"""
    refacciones = Refaccion.objects.filter(activo=True)
    categorias = CategoriaRefaccion.objects.all()
    categoria_filter = request.GET.get('categoria')
    search = request.GET.get('search')
    
    if categoria_filter:
        refacciones = refacciones.filter(categoria_id=categoria_filter)
    if search:
        refacciones = refacciones.filter(
            Q(nombre__icontains=search) | 
            Q(marca__icontains=search) |
            Q(modelo_compatible__icontains=search)
        )
    
    context = {
        'refacciones': refacciones,
        'categorias': categorias,
        'categoria_actual': categoria_filter,
        'search_actual': search,
    }
    return render(request, 'refacciones/lista_refacciones.html', context)

def detalle_refaccion(request, refaccion_id):
    """Vista de detalle de una refacción específica"""
    refaccion = get_object_or_404(Refaccion, id=refaccion_id, activo=True)
    
    # Refacciones relacionadas de la misma categoría
    refacciones_relacionadas = Refaccion.objects.filter(
        categoria=refaccion.categoria,
        activo=True
    ).exclude(id=refaccion_id)[:4]
    
    # Verificar si está en favoritos
    es_favorito = False
    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(usuario=request.user, refaccion=refaccion).exists()
    
    context = {
        'refaccion': refaccion,
        'refacciones_relacionadas': refacciones_relacionadas,
        'es_favorito': es_favorito,
    }
    return render(request, 'refacciones/detalle_refaccion.html', context)

@empleado_required
def panel_empleado(request):
    """Panel de control para empleados"""
    discos_recientes = Disco.objects.all().order_by('-fecha_agregado')[:5]
    instrumentos_recientes = Instrumento.objects.all().order_by('-fecha_agregado')[:5]
    refacciones_recientes = Refaccion.objects.all().order_by('-fecha_agregado')[:5]
    
    total_discos = Disco.objects.count()
    total_instrumentos = Instrumento.objects.count()
    total_refacciones = Refaccion.objects.count()
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    total_ganancias = Pedido.objects.filter(estado__in=['completado', 'enviado']).aggregate(total=Sum('total'))['total'] or 0
    
    context = {
        'discos_recientes': discos_recientes,
        'instrumentos_recientes': instrumentos_recientes,
        'refacciones_recientes': refacciones_recientes,
        'total_discos': total_discos,
        'total_instrumentos': total_instrumentos,
        'total_refacciones': total_refacciones,
        'pedidos_pendientes': pedidos_pendientes,
        'total_ganancias': total_ganancias,
    }
    return render(request, 'empleado/panel.html', context)

@empleado_required
def gestor_banner(request):
    artistas = Artista.objects.all().order_by('nombre')
    if not artistas.exists():
        messages.warning(request, 'No hay artistas cargados todavía. Agrega artistas para configurar el banner.')
        return redirect('panel_empleado')

    if request.method == 'POST':
        artista_id = request.POST.get('artista_id')
    else:
        artista_id = request.GET.get('artista')

    if artista_id:
        artista = get_object_or_404(Artista, id=artista_id)
    else:
        artista = artistas.first()

    banner = getattr(artista, 'hero_banner', None)

    if request.method == 'POST':
        form = HeroBannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            banner = form.save(commit=False)
            banner.artista = artista
            banner.save()
            messages.success(request, f'Banner actualizado para {artista.nombre}.')
            return redirect(f"{reverse('gestor_banner')}?artista={artista.id}")
        else:
            messages.error(request, 'Por favor corrige los errores señalados.')
    else:
        form = HeroBannerForm(instance=banner)

    preview_config = {
        'title': banner.titulo if banner else 'A Destiempo',
        'subtitle': banner.subtitulo if banner else 'Descubre la mejor colección de discos, vinilos e instrumentos musicales. Donde la música cobra vida.',
        'button1_text': banner.boton_1_texto if banner else 'Explorar Discos',
        'button1_url': banner.get_boton_1_url() if banner else reverse('lista_discos'),
        'button2_text': banner.boton_2_texto if banner else 'Ver Instrumentos',
        'button2_url': banner.get_boton_2_url() if banner else reverse('lista_instrumentos'),
        'background_url': banner.imagen.url if banner and banner.imagen else (artista.foto.url if artista.foto else '')
    }

    context = {
        'form': form,
        'artistas': artistas,
        'artista_seleccionado': artista,
        'banner': banner,
        'preview_config': preview_config,
    }
    return render(request, 'empleado/gestor_banner.html', context)

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

def obtener_carrito(request):
    """Obtiene el carrito de la sesión"""
    if 'carrito' not in request.session:
        request.session['carrito'] = []
    return request.session['carrito']

def agregar_al_carrito(request, tipo_producto, producto_id, cantidad=1):
    """Función auxiliar para agregar productos al carrito"""
    carrito = obtener_carrito(request)
    
    # Buscar si el producto ya está en el carrito
    item_existente = None
    for item in carrito:
        if item.get('tipo') == tipo_producto and item.get('id') == producto_id:
            item_existente = item
            break
    
    if item_existente:
        item_existente['cantidad'] += cantidad
    else:
        carrito.append({
            'tipo': tipo_producto,
            'id': producto_id,
            'cantidad': cantidad
        })
    
    request.session['carrito'] = carrito
    request.session.modified = True

@login_required_with_message
def agregar_al_carrito_disco(request, disco_id):
    """Agregar disco al carrito (requiere autenticación)"""
    disco = get_object_or_404(Disco, id=disco_id, activo=True)
    
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        
        if not disco.tiene_stock():
            messages.error(request, f"El disco '{disco.titulo}' no tiene stock disponible.")
            return redirect('detalle_disco', disco_id=disco_id)
        
        agregar_al_carrito(request, 'disco', disco_id, cantidad)
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
        
        agregar_al_carrito(request, 'instrumento', instrumento_id, cantidad)
        messages.success(request, f"¡{instrumento.nombre} agregado al carrito!")
        return redirect('detalle_instrumento', instrumento_id=instrumento_id)
    
    return redirect('detalle_instrumento', instrumento_id=instrumento_id)

@login_required_with_message
def agregar_al_carrito_refaccion(request, refaccion_id):
    """Agregar refacción al carrito (requiere autenticación)"""
    refaccion = get_object_or_404(Refaccion, id=refaccion_id, activo=True)
    
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        
        if not refaccion.tiene_stock():
            messages.error(request, f"La refacción '{refaccion.nombre}' no tiene stock disponible.")
            return redirect('detalle_refaccion', refaccion_id=refaccion_id)
        
        agregar_al_carrito(request, 'refaccion', refaccion_id, cantidad)
        messages.success(request, f"¡{refaccion.nombre} agregado al carrito!")
        return redirect('detalle_refaccion', refaccion_id=refaccion_id)
    
    return redirect('detalle_refaccion', refaccion_id=refaccion_id)

@login_required_with_message
def ver_carrito(request):
    """Ver carrito de compras (requiere autenticación)"""
    carrito = obtener_carrito(request)
    items = []
    subtotal = Decimal('0')
    
    for item in carrito:
        producto = None
        tipo = item.get('tipo')
        producto_id = item.get('id')
        cantidad = item.get('cantidad', 1)
        
        try:
            if tipo == 'disco':
                producto = Disco.objects.get(id=producto_id, activo=True)
            elif tipo == 'instrumento':
                producto = Instrumento.objects.get(id=producto_id, activo=True)
            elif tipo == 'refaccion':
                producto = Refaccion.objects.get(id=producto_id, activo=True)
            
            if producto:
                precio = producto.precio
                item_subtotal = precio * cantidad
                subtotal += item_subtotal
                
                items.append({
                    'tipo': tipo,
                    'producto': producto,
                    'cantidad': cantidad,
                    'precio': precio,
                    'subtotal': item_subtotal,
                    'item_id': len(items)  # Para identificar el item en el carrito
                })
        except:
            continue
    
    impuestos = subtotal * Decimal('0.16')  # IVA 16%
    total = subtotal + impuestos
    
    context = {
        'titulo': 'Mi Carrito',
        'items': items,
        'subtotal': subtotal,
        'impuestos': impuestos,
        'total': total,
    }
    return render(request, 'carrito/carrito.html', context)

@login_required_with_message
@require_POST
def eliminar_del_carrito(request, item_index):
    """Eliminar un item del carrito"""
    carrito = obtener_carrito(request)
    
    try:
        item_index = int(item_index)
        if 0 <= item_index < len(carrito):
            item = carrito.pop(item_index)
            request.session['carrito'] = carrito
            request.session.modified = True
            messages.success(request, 'Item eliminado del carrito.')
    except:
        messages.error(request, 'Error al eliminar el item.')
    
    return redirect('carrito')

@login_required_with_message
@require_POST
def actualizar_cantidad_carrito(request, item_index):
    """Actualizar cantidad de un item en el carrito"""
    carrito = obtener_carrito(request)
    
    try:
        item_index = int(item_index)
        nueva_cantidad = int(request.POST.get('cantidad', 1))
        
        if 0 <= item_index < len(carrito) and nueva_cantidad > 0:
            carrito[item_index]['cantidad'] = nueva_cantidad
            request.session['carrito'] = carrito
            request.session.modified = True
            messages.success(request, 'Cantidad actualizada.')
    except:
        messages.error(request, 'Error al actualizar la cantidad.')
    
    return redirect('carrito')

@login_required_with_message
def checkout(request):
    """Proceso de checkout (requiere autenticación)"""
    carrito = obtener_carrito(request)
    
    if not carrito:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('carrito')
    
    # Validar que todos los items aún existan y tengan stock
    items_validos = []
    subtotal = Decimal('0')
    
    for item in carrito:
        tipo = item.get('tipo')
        producto_id = item.get('id')
        cantidad = item.get('cantidad', 1)
        
        try:
            producto = None
            if tipo == 'disco':
                producto = Disco.objects.get(id=producto_id, activo=True)
            elif tipo == 'instrumento':
                producto = Instrumento.objects.get(id=producto_id, activo=True)
            elif tipo == 'refaccion':
                producto = Refaccion.objects.get(id=producto_id, activo=True)
            
            if producto and producto.tiene_stock():
                precio = producto.precio
                item_subtotal = precio * cantidad
                subtotal += item_subtotal
                items_validos.append({
                    'tipo': tipo,
                    'producto': producto,
                    'cantidad': cantidad,
                    'precio': precio,
                    'subtotal': item_subtotal
                })
        except:
            continue
    
    if not items_validos:
        messages.error(request, 'No hay items válidos en tu carrito.')
        request.session['carrito'] = []
        return redirect('carrito')
    
    impuestos = subtotal * Decimal('0.16')
    total = subtotal + impuestos
    
    # Obtener datos del usuario para prellenar el formulario
    usuario = request.user
    perfil = getattr(usuario, 'perfilusuario', None)
    
    if request.method == 'POST':
        # Crear el pedido
        try:
            pedido = Pedido.objects.create(
                cliente=usuario,
                nombre_completo=request.POST.get('nombre_completo'),
                direccion=request.POST.get('direccion'),
                ciudad=request.POST.get('ciudad'),
                codigo_postal=request.POST.get('codigo_postal', ''),
                telefono=request.POST.get('telefono'),
                email=request.POST.get('email', usuario.email),
                metodo_pago=request.POST.get('metodo_pago', 'transferencia'),
                pagado=True,  # Simulado
                fecha_pago=datetime.now(),
                subtotal=subtotal,
                impuestos=impuestos,
                total=total
            )
            
            # Crear items del pedido
            for item in items_validos:
                ItemPedido.objects.create(
                    pedido=pedido,
                    disco=item['producto'] if item['tipo'] == 'disco' else None,
                    instrumento=item['producto'] if item['tipo'] == 'instrumento' else None,
                    refaccion=item['producto'] if item['tipo'] == 'refaccion' else None,
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio'],
                    subtotal=item['subtotal']
                )
            
            # Limpiar carrito
            request.session['carrito'] = []
            request.session.modified = True
            
            # Enviar factura por email
            try:
                enviar_factura_email(pedido)
                pedido.factura_enviada = True
                pedido.fecha_factura_enviada = datetime.now()
                pedido.save(update_fields=['factura_enviada', 'fecha_factura_enviada'])
            except Exception as e:
                print(f"Error al enviar factura por email: {e}")
                messages.warning(request, f'Pedido creado exitosamente, pero no se pudo enviar la factura por email.')
            
            messages.success(request, f'¡Pedido #{pedido.numero_pedido} creado exitosamente!')
            return redirect('detalle_pedido', pedido_id=pedido.id)
            
        except Exception as e:
            messages.error(request, f'Error al crear el pedido: {str(e)}')
    
    context = {
        'titulo': 'Finalizar Compra',
        'items': items_validos,
        'subtotal': subtotal,
        'impuestos': impuestos,
        'total': total,
        'nombre_completo': usuario.get_full_name() or usuario.username,
        'email': usuario.email,
        'telefono': perfil.telefono if perfil else '',
        'direccion': perfil.direccion if perfil else '',
    }
    return render(request, 'carrito/checkout.html', context)


@login_required_with_message
@require_POST
def agregar_favorito_disco(request, disco_id):
    """Agregar disco a favoritos (requiere autenticación)"""
    disco = get_object_or_404(Disco, id=disco_id, activo=True)
    favorito, created = Favorito.objects.get_or_create(
        usuario=request.user,
        disco=disco,
        defaults={'disco': disco}
    )
    if created:
        messages.success(request, f'¡"{disco.titulo}" agregado a favoritos!')
    else:
        messages.info(request, f'"{disco.titulo}" ya está en tus favoritos.')
    return redirect('detalle_disco', disco_id=disco_id)

@login_required_with_message
@require_POST
def quitar_favorito_disco(request, disco_id):
    """Quitar disco de favoritos (requiere autenticación)"""
    disco = get_object_or_404(Disco, id=disco_id)
    Favorito.objects.filter(usuario=request.user, disco=disco).delete()
    messages.success(request, f'"{disco.titulo}" eliminado de favoritos.')
    return redirect('detalle_disco', disco_id=disco_id)

@login_required_with_message
@require_POST
def agregar_favorito_instrumento(request, instrumento_id):
    """Agregar instrumento a favoritos (requiere autenticación)"""
    instrumento = get_object_or_404(Instrumento, id=instrumento_id, activo=True)
    favorito, created = Favorito.objects.get_or_create(
        usuario=request.user,
        instrumento=instrumento,
        defaults={'instrumento': instrumento}
    )
    if created:
        messages.success(request, f'¡"{instrumento.nombre}" agregado a favoritos!')
    else:
        messages.info(request, f'"{instrumento.nombre}" ya está en tus favoritos.')
    return redirect('detalle_instrumento', instrumento_id=instrumento_id)

@login_required_with_message
@require_POST
def quitar_favorito_instrumento(request, instrumento_id):
    """Quitar instrumento de favoritos (requiere autenticación)"""
    instrumento = get_object_or_404(Instrumento, id=instrumento_id)
    Favorito.objects.filter(usuario=request.user, instrumento=instrumento).delete()
    messages.success(request, f'"{instrumento.nombre}" eliminado de favoritos.')
    return redirect('detalle_instrumento', instrumento_id=instrumento_id)

@login_required_with_message
@require_POST
def agregar_favorito_refaccion(request, refaccion_id):
    """Agregar refacción a favoritos (requiere autenticación)"""
    refaccion = get_object_or_404(Refaccion, id=refaccion_id, activo=True)
    favorito, created = Favorito.objects.get_or_create(
        usuario=request.user,
        refaccion=refaccion,
        defaults={'refaccion': refaccion}
    )
    if created:
        messages.success(request, f'¡"{refaccion.nombre}" agregado a favoritos!')
    else:
        messages.info(request, f'"{refaccion.nombre}" ya está en tus favoritos.')
    return redirect('detalle_refaccion', refaccion_id=refaccion_id)

@login_required_with_message
@require_POST
def quitar_favorito_refaccion(request, refaccion_id):
    """Quitar refacción de favoritos (requiere autenticación)"""
    refaccion = get_object_or_404(Refaccion, id=refaccion_id)
    Favorito.objects.filter(usuario=request.user, refaccion=refaccion).delete()
    messages.success(request, f'"{refaccion.nombre}" eliminado de favoritos.')
    return redirect('detalle_refaccion', refaccion_id=refaccion_id)

@login_required(login_url='/accounts/login/')
def mis_favoritos(request):
    """Vista para ver favoritos del usuario"""
    favoritos = Favorito.objects.filter(usuario=request.user).order_by('-fecha_agregado')
    context = {
        'favoritos': favoritos,
        'titulo': 'Mis Favoritos',
    }
    return render(request, 'cliente/favoritos.html', context)

@login_required_with_message
def ver_factura(request, pedido_id):
    """Vista para ver la factura del pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    context = {
        'pedido': pedido,
    }
    return render(request, 'facturas/factura.html', context)

@login_required_with_message
def detalle_pedido(request, pedido_id):
    """Vista de detalle de un pedido para el cliente"""
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    context = {
        'pedido': pedido,
        'titulo': f'Pedido #{pedido.numero_pedido}',
    }
    return render(request, 'cliente/detalle_pedido.html', context)

@login_required_with_message
def mis_pedidos(request):
    """Vista para ver todos los pedidos del cliente"""
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-fecha_pedido')
    context = {
        'pedidos': pedidos,
        'titulo': 'Mis Pedidos',
    }
    return render(request, 'cliente/mis_pedidos.html', context)

@login_required_with_message
def historial_pedidos(request):
    """Vista de historial completo de pedidos del cliente"""
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-fecha_pedido')
    pedidos_por_estado = pedidos.values('estado').annotate(total=Count('id'))
    total_gastado = pedidos.aggregate(total=Sum('total'))['total'] or Decimal('0')

    context = {
        'titulo': 'Historial de Pedidos',
        'pedidos': pedidos,
        'resumen_estados': pedidos_por_estado,
        'total_gastado': total_gastado,
    }
    return render(request, 'cliente/historial_pedidos.html', context)


@empleado_required
def buscar_metadatos_ajax(request):
    """Vista AJAX para buscar metadatos de discos"""
    if request.method == 'GET':
        titulo = request.GET.get('titulo', '').strip()
        artista = request.GET.get('artista', '').strip()
        
        if not titulo:
            return JsonResponse({'error': 'Título requerido'}, status=400)
        
        # Buscar metadatos
        resultados = buscar_metadatos_disco(titulo, artista if artista else None)
        
        # Formatear resultados para JSON
        resultados_formateados = []
        for resultado in resultados:
            resultados_formateados.append({
                'titulo': resultado.get('titulo', ''),
                'titulo_completo': resultado.get('titulo_completo', resultado.get('titulo', '')),
                'artista': resultado.get('artista', ''),
                'artistas_lista': resultado.get('artistas_lista', []),
                'año': resultado.get('año'),
                'fecha': resultado.get('fecha', ''),
                'generos': resultado.get('generos', []),
                'cover_art_url': resultado.get('cover_art_url', ''),
                'musicbrainz_id': resultado.get('musicbrainz_id', ''),
                'version': resultado.get('version', ''),
                'edicion': resultado.get('edicion', ''),
                'tags': resultado.get('tags', []),
            })
        
        return JsonResponse({
            'success': True,
            'resultados': resultados_formateados,
            'total': len(resultados_formateados)
        })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@empleado_required
def lista_discos_vendedor(request):
    """Lista todos los discos para el vendedor (sin usar admin)"""
    discos = Disco.objects.all().order_by('-fecha_agregado')
    
    # Filtros
    search = request.GET.get('search', '')
    formato_filter = request.GET.get('formato', '')
    genero_filter = request.GET.get('genero', '')
    artista_filter = request.GET.get('artista', '')
    activo_filter = request.GET.get('activo', '')
    
    if search:
        discos = discos.filter(
            Q(titulo__icontains=search) | 
            Q(artista__nombre__icontains=search)
        )
    
    if formato_filter:
        discos = discos.filter(formato=formato_filter)
    
    if genero_filter:
        discos = discos.filter(genero=genero_filter)
    
    if artista_filter:
        discos = discos.filter(artista_id=artista_filter)
    
    if activo_filter != '':
        if activo_filter == 'si':
            discos = discos.filter(activo=True)
        elif activo_filter == 'no':
            discos = discos.filter(activo=False)
    
    # Obtener opciones para filtros
    generos = Genero.objects.all().order_by('nombre')
    artistas = Artista.objects.all().order_by('nombre')
    
    context = {
        'discos': discos,
        'generos': generos,
        'artistas': artistas,
        'search_actual': search,
        'formato_actual': formato_filter,
        'genero_actual': genero_filter,
        'artista_actual': artista_filter,
        'activo_actual': activo_filter,
        'titulo': 'Gestión de Discos',
    }
    return render(request, 'empleado/lista_discos.html', context)

@empleado_required
def lista_instrumentos_vendedor(request):
    """Lista todos los instrumentos para el vendedor"""
    instrumentos = Instrumento.objects.all().order_by('-fecha_agregado')

    search = request.GET.get('search', '')
    categoria_filter = request.GET.get('categoria', '')
    estado_filter = request.GET.get('estado', '')
    activo_filter = request.GET.get('activo', '')

    if search:
        instrumentos = instrumentos.filter(
            Q(nombre__icontains=search) |
            Q(marca__icontains=search) |
            Q(modelo__icontains=search)
        )

    if categoria_filter:
        instrumentos = instrumentos.filter(categoria_id=categoria_filter)

    if estado_filter:
        instrumentos = instrumentos.filter(estado=estado_filter)

    if activo_filter != '':
        if activo_filter == 'si':
            instrumentos = instrumentos.filter(activo=True)
        elif activo_filter == 'no':
            instrumentos = instrumentos.filter(activo=False)

    categorias = CategoriaInstrumento.objects.all().order_by('nombre')

    context = {
        'instrumentos': instrumentos,
        'categorias': categorias,
        'search_actual': search,
        'categoria_actual': categoria_filter,
        'estado_actual': estado_filter,
        'activo_actual': activo_filter,
        'titulo': 'Gestión de Instrumentos',
    }
    return render(request, 'empleado/lista_instrumentos.html', context)

@empleado_required
def lista_refacciones_vendedor(request):
    """Lista todas las refacciones para el vendedor"""
    refacciones = Refaccion.objects.all().order_by('-fecha_agregado')

    search = request.GET.get('search', '')
    categoria_filter = request.GET.get('categoria', '')
    activo_filter = request.GET.get('activo', '')

    if search:
        refacciones = refacciones.filter(
            Q(nombre__icontains=search) |
            Q(marca__icontains=search) |
            Q(modelo_compatible__icontains=search)
        )

    if categoria_filter:
        refacciones = refacciones.filter(categoria_id=categoria_filter)

    if activo_filter != '':
        if activo_filter == 'si':
            refacciones = refacciones.filter(activo=True)
        elif activo_filter == 'no':
            refacciones = refacciones.filter(activo=False)

    categorias = CategoriaRefaccion.objects.all().order_by('nombre')

    context = {
        'refacciones': refacciones,
        'categorias': categorias,
        'search_actual': search,
        'categoria_actual': categoria_filter,
        'activo_actual': activo_filter,
        'titulo': 'Gestión de Refacciones',
    }
    return render(request, 'empleado/lista_refacciones.html', context)

@empleado_required
def crear_disco(request):
    """Crear nuevo disco"""
    # Obtener artistas existentes para autocomplete
    artistas_existentes = Artista.objects.all().order_by('nombre')[:50]
    
    if request.method == 'POST':
        form = DiscoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                disco = form.save(commit=False)
                
                # Si se proporcionó una URL de portada, descargarla ANTES de guardar
                cover_url = request.POST.get('cover_art_url', '').strip()
                if cover_url:
                    try:
                        cover_file = descargar_portada(cover_url, disco.titulo, disco.artista.nombre)
                        if cover_file:
                            # Asignar el ContentFile directamente al ImageField
                            # Django se encargará de guardarlo usando upload_to
                            disco.portada.save(cover_file.name, cover_file, save=False)
                            print(f"Portada asignada al disco: {disco.portada.name}")
                        else:
                            messages.warning(request, 'No se pudo descargar la portada desde la URL proporcionada.')
                    except Exception as e:
                        print(f"Error al descargar portada: {e}")
                        import traceback
                        traceback.print_exc()
                        messages.warning(request, f'Error al descargar la portada: {str(e)}')
                
                # Guardar el disco con la portada
                disco.save()
                print(f"Disco guardado con portada: {disco.portada}")
                
                # Guardar stock para el formato seleccionado
                from .models import Inventario, Sucursal
                try:
                    sucursal_principal = Sucursal.objects.get(nombre='Principal')
                except Sucursal.DoesNotExist:
                    sucursal_principal = Sucursal.objects.create(nombre='Principal', activa=True)
                
                # Obtener el formato del disco
                formato = disco.formato
                stock = form.cleaned_data.get('stock', 0) or 0
                
                # Guardar o actualizar el inventario para este formato
                inventario, created = Inventario.objects.get_or_create(
                    producto_disco=disco,
                    formato_disco=formato,
                    sucursal=sucursal_principal,
                    defaults={'stock_disponible': stock}
                )
                if not created:
                    inventario.stock_disponible = stock
                    inventario.save()
                
                messages.success(request, f'¡Disco "{disco.titulo}" creado exitosamente!')
                return redirect('panel_empleado')
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                messages.error(request, f'Error al guardar el disco: {str(e)}')
                print(f"Error completo: {error_detail}")
        else:
            # Mostrar errores del formulario
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            messages.error(request, 'Error al crear el disco. ' + ' '.join(error_messages[:3]))
    else:
        form = DiscoForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Disco',
        'artistas_existentes': artistas_existentes
    }
    return render(request, 'empleado/disco_form.html', context)

@empleado_required
def editar_disco(request, disco_id):
    """Editar disco existente"""
    disco = get_object_or_404(Disco, id=disco_id)
    # Obtener artistas existentes para autocomplete
    artistas_existentes = Artista.objects.all().order_by('nombre')[:50]
    
    if request.method == 'POST':
        form = DiscoForm(request.POST, request.FILES, instance=disco)
        if form.is_valid():
            try:
                disco = form.save(commit=False)
                
                # Si se proporcionó una URL de portada nueva, descargarla ANTES de guardar
                cover_url = request.POST.get('cover_art_url', '').strip()
                if cover_url:
                    try:
                        cover_file = descargar_portada(cover_url, disco.titulo, disco.artista.nombre)
                        if cover_file:
                            # Asignar el ContentFile directamente al ImageField
                            # Django se encargará de guardarlo usando upload_to
                            disco.portada.save(cover_file.name, cover_file, save=False)
                            print(f"Portada asignada al disco: {disco.portada.name}")
                        else:
                            messages.warning(request, 'No se pudo descargar la portada desde la URL proporcionada.')
                    except Exception as e:
                        print(f"Error al descargar portada: {e}")
                        import traceback
                        traceback.print_exc()
                        messages.warning(request, f'Error al descargar la portada: {str(e)}')
                
                # Guardar el disco con la portada
                disco.save()
                
                # Guardar stock para el formato seleccionado
                from .models import Inventario, Sucursal
                try:
                    sucursal_principal = Sucursal.objects.get(nombre='Principal')
                except Sucursal.DoesNotExist:
                    sucursal_principal = Sucursal.objects.create(nombre='Principal', activa=True)
                
                # Obtener el formato del disco
                formato = disco.formato
                stock = form.cleaned_data.get('stock', 0) or 0
                
                # Guardar o actualizar el inventario para este formato
                inventario, created = Inventario.objects.get_or_create(
                    producto_disco=disco,
                    formato_disco=formato,
                    sucursal=sucursal_principal,
                    defaults={'stock_disponible': stock}
                )
                if not created:
                    inventario.stock_disponible = stock
                    inventario.save()
                
                messages.success(request, f'¡Disco "{disco.titulo}" actualizado exitosamente!')
                return redirect('panel_empleado')
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                messages.error(request, f'Error al actualizar el disco: {str(e)}')
                print(f"Error completo: {error_detail}")
        else:
            # Mostrar errores del formulario
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            messages.error(request, 'Error al actualizar el disco. ' + ' '.join(error_messages[:3]))
    else:
        form = DiscoForm(instance=disco)
    
    context = {
        'form': form,
        'disco': disco,
        'titulo': 'Editar Disco',
        'artistas_existentes': artistas_existentes
    }
    return render(request, 'empleado/disco_form.html', context)

@empleado_required
def eliminar_disco(request, disco_id):
    """Eliminar disco (marcar como inactivo para que no aparezca en ningún lugar)"""
    disco = get_object_or_404(Disco, id=disco_id)
    
    if request.method == 'POST':
        titulo = disco.titulo
        # Marcar como inactivo en lugar de eliminar físicamente
        # Esto asegura que no aparezca en ningún lugar (página principal, listados, etc.)
        disco.activo = False
        disco.save()
        messages.success(request, f'¡Disco "{titulo}" eliminado del catálogo exitosamente!')
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

@empleado_required
def crear_refaccion(request):
    """Crear nueva refacción"""
    if request.method == 'POST':
        form = RefaccionForm(request.POST, request.FILES)
        if form.is_valid():
            refaccion = form.save()
            messages.success(request, f'¡Refacción "{refaccion.nombre}" creada exitosamente!')
            return redirect('panel_empleado')
    else:
        form = RefaccionForm()
    
    return render(request, 'empleado/refaccion_form.html', {'form': form, 'titulo': 'Crear Refacción'})

@empleado_required
def editar_refaccion(request, refaccion_id):
    """Editar refacción existente"""
    refaccion = get_object_or_404(Refaccion, id=refaccion_id)
    
    if request.method == 'POST':
        form = RefaccionForm(request.POST, request.FILES, instance=refaccion)
        if form.is_valid():
            refaccion = form.save()
            messages.success(request, f'¡Refacción "{refaccion.nombre}" actualizada exitosamente!')
            return redirect('panel_empleado')
    else:
        form = RefaccionForm(instance=refaccion)
    
    return render(request, 'empleado/refaccion_form.html', {'form': form, 'refaccion': refaccion, 'titulo': 'Editar Refacción'})

@empleado_required
def eliminar_refaccion(request, refaccion_id):
    """Eliminar refacción"""
    refaccion = get_object_or_404(Refaccion, id=refaccion_id)
    
    if request.method == 'POST':
        nombre = refaccion.nombre
        refaccion.delete()
        messages.success(request, f'¡Refacción "{nombre}" eliminada exitosamente!')
        return redirect('panel_empleado')
    
    return render(request, 'empleado/confirmar_eliminar.html', {'objeto': refaccion, 'tipo': 'refaccion'})


@empleado_required
def panel_reportes(request):
    """Panel de reportes para vendedor"""
    pedidos_completados = Pedido.objects.filter(estado__in=['completado', 'enviado'])
    total_ganancias = pedidos_completados.aggregate(total=Sum('total'))['total'] or 0
    total_pedidos = pedidos_completados.count()
    
    compras_recientes = pedidos_completados.order_by('-fecha_pedido')[:20]
    
    usuarios_activos = User.objects.filter(pedidos__isnull=False).distinct().count()
    
    items_mas_vendidos = ItemPedido.objects.filter(
        pedido__estado__in=['completado', 'enviado']
    ).values('disco__titulo', 'disco__artista__nombre', 'instrumento__nombre', 'instrumento__marca', 'refaccion__nombre', 'refaccion__marca').annotate(
        total_vendido=Sum('cantidad'),
        total_ganancia=Sum('subtotal')
    ).order_by('-total_vendido')[:10]
    
    context = {
        'total_ganancias': total_ganancias,
        'total_pedidos': total_pedidos,
        'compras_recientes': compras_recientes,
        'usuarios_activos': usuarios_activos,
        'items_mas_vendidos': items_mas_vendidos,
        'titulo': 'Panel de Reportes',
    }
    return render(request, 'empleado/reportes.html', context)

@empleado_required
def lista_clientes(request):
    """CRUD de clientes para vendedor"""
    clientes = User.objects.filter(perfilusuario__tipo_usuario='cliente').order_by('-date_joined')
    search = request.GET.get('search', '')
    
    if search:
        clientes = clientes.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    context = {
        'clientes': clientes,
        'search_actual': search,
        'titulo': 'Gestión de Clientes',
    }
    return render(request, 'empleado/clientes.html', context)

@empleado_required
def detalle_cliente(request, cliente_id):
    """Detalle de un cliente para vendedor"""
    cliente = get_object_or_404(User, id=cliente_id)
    pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha_pedido')
    total_gastado = pedidos.aggregate(total=Sum('total'))['total'] or 0
    
    context = {
        'cliente': cliente,
        'pedidos': pedidos,
        'total_gastado': total_gastado,
        'titulo': f'Cliente: {cliente.username}',
    }
    return render(request, 'empleado/detalle_cliente.html', context)

@empleado_required
@require_http_methods(["POST"])
def generar_reporte_clientes_pdf(request):
    """Genera un reporte PDF con los clientes seleccionados"""
    try:
        clientes_ids = request.POST.getlist('clientes_seleccionados')
        
        if not clientes_ids:
            messages.error(request, 'Por favor selecciona al menos un cliente para generar el reporte.')
            return redirect('lista_clientes')
        
        clientes = User.objects.filter(
            id__in=clientes_ids,
            perfilusuario__tipo_usuario='cliente'
        ).order_by('username')
        
        if not clientes.exists():
            messages.error(request, 'No se encontraron clientes válidos.')
            return redirect('lista_clientes')
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_clientes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=A4)
        story = []
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#00d4aa'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1db954'),
            spaceAfter=20,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        )
        
        report_subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1db954'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#000000'),
            spaceAfter=12,
            alignment=TA_LEFT,
            fontName='Helvetica'
        )
        
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#333333'),
            spaceAfter=8,
            alignment=TA_LEFT,
            fontName='Helvetica'
        )
        
        title = Paragraph("A DESTIEMPO", title_style)
        story.append(title)
        
        subtitle = Paragraph("REPORTE DE CLIENTES", report_subtitle_style)
        story.append(subtitle)
        
        fecha_reporte = datetime.now().strftime("%d/%m/%Y %H:%M")
        info_text = f"<b>Fecha de generación:</b> {fecha_reporte}<br/>"
        info_text += f"<b>Total de clientes:</b> {clientes.count()}"
        info_paragraph = Paragraph(info_text, normal_style)
        story.append(info_paragraph)
        story.append(Spacer(1, 0.3*inch))
        
        for idx, cliente in enumerate(clientes, 1):
            pedidos = Pedido.objects.filter(cliente=cliente)
            total_pedidos = pedidos.count()
            total_gastado = pedidos.aggregate(total=Sum('total'))['total'] or 0
            
            cliente_title = f"<b>Cliente #{idx}: {cliente.username}</b>"
            cliente_paragraph = Paragraph(cliente_title, subtitle_style)
            story.append(cliente_paragraph)
            
            cliente_data = [
                ['<b>Usuario:</b>', cliente.username],
                ['<b>Nombre completo:</b>', cliente.get_full_name() or '-'],
                ['<b>Email:</b>', cliente.email],
                ['<b>Fecha de registro:</b>', cliente.date_joined.strftime("%d/%m/%Y %H:%M")],
                ['<b>Último acceso:</b>', cliente.last_login.strftime("%d/%m/%Y %H:%M") if cliente.last_login else 'Nunca'],
                ['<b>Total de pedidos:</b>', str(total_pedidos)],
                ['<b>Total gastado:</b>', f"${total_gastado:,.2f}"],
            ]
            
            cliente_table = Table(cliente_data, colWidths=[2.5*inch, 4*inch])
            cliente_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1a1a1a')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#00d4aa')),
                ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f5f5f5')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#000000')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ]))
            
            story.append(cliente_table)
            story.append(Spacer(1, 0.4*inch))
            
            if total_pedidos > 0:
                pedidos_text = f"<b>Historial de pedidos:</b> {total_pedidos} pedido(s) realizados"
                pedidos_paragraph = Paragraph(pedidos_text, info_style)
                story.append(pedidos_paragraph)
                story.append(Spacer(1, 0.2*inch))
            
            if idx < clientes.count():
                story.append(Spacer(1, 0.2*inch))
                separador = Table([['']], colWidths=[6.5*inch], rowHeights=[0.02*inch])
                separador.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#00d4aa')),
                ]))
                story.append(separador)
                story.append(Spacer(1, 0.3*inch))
        
        story.append(Spacer(1, 0.5*inch))
        footer_text = f"<i>Reporte generado el {fecha_reporte} - A Destiempo - Sistema de Gestión</i>"
        footer_paragraph = Paragraph(footer_text, info_style)
        story.append(footer_paragraph)
        
        doc.build(story)
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error al generar el reporte: {str(e)}')
        import traceback
        traceback.print_exc()
        return redirect('lista_clientes')

@empleado_required
def pedidos_pendientes(request):
    """CRUD de pedidos pendientes para vendedor"""
    estado_filter = request.GET.get('estado', 'pendiente')
    
    if estado_filter == 'todos':
        pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    else:
        pedidos = Pedido.objects.filter(estado=estado_filter).order_by('-fecha_pedido')
    
    context = {
        'pedidos': pedidos,
        'estado_actual': estado_filter,
        'titulo': 'Gestión de Pedidos',
    }
    return render(request, 'empleado/pedidos.html', context)

@empleado_required
def detalle_pedido_vendedor(request, pedido_id):
    """Detalle de un pedido para vendedor (con opción de cambiar estado)"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Pedido.ESTADOS_PEDIDO):
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f'Estado del pedido actualizado a: {pedido.get_estado_display()}')
            return redirect('detalle_pedido_vendedor', pedido_id=pedido_id)
    
    context = {
        'pedido': pedido,
        'titulo': f'Pedido #{pedido.numero_pedido}',
    }
    return render(request, 'empleado/detalle_pedido.html', context)


def enviar_factura_email(pedido):
    """Envía la factura del pedido por email al cliente"""
    try:
        html_content = render_to_string('facturas/factura.html', {'pedido': pedido})
        
        subject = f'Factura - Pedido #{pedido.numero_pedido} - A Destiempo'
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@adestiempo.com')
        to_email = pedido.email
        
        msg = EmailMultiAlternatives(subject, '', from_email, [to_email])
        msg.attach_alternative(html_content, 'text/html')
        
        msg.send()
        
        print(f"Factura enviada por email a {to_email} para el pedido #{pedido.numero_pedido}")
        return True
    except Exception as e:
        print(f"Error al enviar factura por email: {e}")
        import traceback
        traceback.print_exc()
        return False

@csrf_exempt
def chat_bot_api(request):
    """API para el bot de chat - procesa mensajes y devuelve respuestas"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        mensaje = data.get('mensaje', '').strip()
        
        if not mensaje:
            return JsonResponse({'error': 'Mensaje vacío'}, status=400)
        
        bot = ChatBot()
        respuesta = bot.procesar_mensaje(mensaje)
        
        return JsonResponse({
            'respuesta': respuesta,
            'exito': True
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': 'Error al procesar el mensaje',
            'respuesta': 'Lo siento, hubo un error. Por favor intenta nuevamente.',
            'exito': False
        }, status=500)
