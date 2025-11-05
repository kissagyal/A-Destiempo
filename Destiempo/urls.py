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
    path('disco/<int:disco_id>/', views.detalle_disco, name='detalle_disco'),
    path('instrumento/<int:instrumento_id>/', views.detalle_instrumento, name='detalle_instrumento'),
    path('panel-empleado/', views.panel_empleado, name='panel_empleado'),
    # CRUDs para vendedor
    path('panel-empleado/buscar-metadatos/', views.buscar_metadatos_ajax, name='buscar_metadatos'),
    path('panel-empleado/disco/crear/', views.crear_disco, name='crear_disco'),
    path('panel-empleado/disco/<int:disco_id>/editar/', views.editar_disco, name='editar_disco'),
    path('panel-empleado/disco/<int:disco_id>/eliminar/', views.eliminar_disco, name='eliminar_disco'),
    path('panel-empleado/instrumento/crear/', views.crear_instrumento, name='crear_instrumento'),
    path('panel-empleado/instrumento/<int:instrumento_id>/editar/', views.editar_instrumento, name='editar_instrumento'),
    path('panel-empleado/instrumento/<int:instrumento_id>/eliminar/', views.eliminar_instrumento, name='eliminar_instrumento'),
    # Carrito y compra (requieren autenticación)
    path('carrito/', views.ver_carrito, name='carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('disco/<int:disco_id>/agregar/', views.agregar_al_carrito_disco, name='agregar_carrito_disco'),
    path('instrumento/<int:instrumento_id>/agregar/', views.agregar_al_carrito_instrumento, name='agregar_carrito_instrumento'),
    # Autenticación personalizada
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
