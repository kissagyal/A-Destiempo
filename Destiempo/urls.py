"""
URL configuration for Destiempo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from tasks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('signup/', views.helloworld, name='signup'),
    path('discos/', views.lista_discos, name='lista_discos'),
    path('instrumentos/', views.lista_instrumentos, name='lista_instrumentos'),
    path('refacciones/', views.lista_refacciones, name='lista_refacciones'),
    path('disco/<int:disco_id>/', views.detalle_disco, name='detalle_disco'),
    path('instrumento/<int:instrumento_id>/', views.detalle_instrumento, name='detalle_instrumento'),
    path('refaccion/<int:refaccion_id>/', views.detalle_refaccion, name='detalle_refaccion'),
    path('panel-empleado/', views.panel_empleado, name='panel_empleado'),
    path('panel-empleado/gestor-banner/', views.gestor_banner, name='gestor_banner'),
    path('panel-empleado/reportes/', views.panel_reportes, name='panel_reportes'),
    path('panel-empleado/clientes/', views.lista_clientes, name='lista_clientes'),
    path('panel-empleado/cliente/<int:cliente_id>/', views.detalle_cliente, name='detalle_cliente'),
    path('panel-empleado/clientes/reporte-pdf/', views.generar_reporte_clientes_pdf, name='generar_reporte_clientes_pdf'),
    path('panel-empleado/pedidos/', views.pedidos_pendientes, name='pedidos_pendientes'),
    path('panel-empleado/pedido/<int:pedido_id>/', views.detalle_pedido_vendedor, name='detalle_pedido_vendedor'),
    # CRUDs para vendedor
    path('panel-empleado/buscar-metadatos/', views.buscar_metadatos_ajax, name='buscar_metadatos'),
    path('panel-empleado/discos/', views.lista_discos_vendedor, name='lista_discos_vendedor'),
    path('panel-empleado/instrumentos/', views.lista_instrumentos_vendedor, name='lista_instrumentos_vendedor'),
    path('panel-empleado/refacciones/', views.lista_refacciones_vendedor, name='lista_refacciones_vendedor'),
    path('panel-empleado/disco/crear/', views.crear_disco, name='crear_disco'),
    path('panel-empleado/disco/<int:disco_id>/editar/', views.editar_disco, name='editar_disco'),
    path('panel-empleado/disco/<int:disco_id>/eliminar/', views.eliminar_disco, name='eliminar_disco'),
    path('panel-empleado/instrumento/crear/', views.crear_instrumento, name='crear_instrumento'),
    path('panel-empleado/instrumento/<int:instrumento_id>/editar/', views.editar_instrumento, name='editar_instrumento'),
    path('panel-empleado/instrumento/<int:instrumento_id>/eliminar/', views.eliminar_instrumento, name='eliminar_instrumento'),
    path('panel-empleado/refaccion/crear/', views.crear_refaccion, name='crear_refaccion'),
    path('panel-empleado/refaccion/<int:refaccion_id>/editar/', views.editar_refaccion, name='editar_refaccion'),
    path('panel-empleado/refaccion/<int:refaccion_id>/eliminar/', views.eliminar_refaccion, name='eliminar_refaccion'),
    # Carrito y compra (requieren autenticación)
    path('carrito/', views.ver_carrito, name='carrito'),
    path('carrito/eliminar/<int:item_index>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/actualizar/<int:item_index>/', views.actualizar_cantidad_carrito, name='actualizar_cantidad_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('disco/<int:disco_id>/agregar/', views.agregar_al_carrito_disco, name='agregar_carrito_disco'),
    path('instrumento/<int:instrumento_id>/agregar/', views.agregar_al_carrito_instrumento, name='agregar_carrito_instrumento'),
    path('refaccion/<int:refaccion_id>/agregar/', views.agregar_al_carrito_refaccion, name='agregar_carrito_refaccion'),
    # Favoritos (requieren autenticación)
    path('mis-favoritos/', views.mis_favoritos, name='mis_favoritos'),
    path('disco/<int:disco_id>/favorito/agregar/', views.agregar_favorito_disco, name='agregar_favorito_disco'),
    path('disco/<int:disco_id>/favorito/quitar/', views.quitar_favorito_disco, name='quitar_favorito_disco'),
    path('instrumento/<int:instrumento_id>/favorito/agregar/', views.agregar_favorito_instrumento, name='agregar_favorito_instrumento'),
    path('instrumento/<int:instrumento_id>/favorito/quitar/', views.quitar_favorito_instrumento, name='quitar_favorito_instrumento'),
    path('refaccion/<int:refaccion_id>/favorito/agregar/', views.agregar_favorito_refaccion, name='agregar_favorito_refaccion'),
    path('refaccion/<int:refaccion_id>/favorito/quitar/', views.quitar_favorito_refaccion, name='quitar_favorito_refaccion'),
    # Pedidos del cliente
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('mis-pedidos/historial/', views.historial_pedidos, name='historial_pedidos'),
    path('pedido/<int:pedido_id>/factura/', views.ver_factura, name='ver_factura'),
    # Autenticación personalizada
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    # Chat Bot API
    path('api/chat/', views.chat_bot_api, name='chat_bot_api'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
