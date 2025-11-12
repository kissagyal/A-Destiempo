from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    PerfilUsuario, Genero, Artista, Disco, 
    CategoriaInstrumento, Instrumento, Sucursal, 
    Inventario, InventarioMovimiento
)

# Inline admin para el perfil de usuario
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'

# Extender el admin de User para incluir el perfil
class CustomUserAdmin(UserAdmin):
    inlines = (PerfilUsuarioInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo_usuario', 'telefono', 'fecha_registro')
    list_filter = ('tipo_usuario', 'fecha_registro')
    search_fields = ('user__username', 'user__email', 'telefono')

@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Artista)
class ArtistaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'foto')
    search_fields = ('nombre',)
    list_filter = ('nombre',)

class DiscoInline(admin.TabularInline):
    model = Disco
    extra = 0
    fields = ('titulo', 'formato', 'precio', 'stock', 'activo')

@admin.register(Disco)
class DiscoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'artista', 'formato', 'precio', 'stock', 'activo')
    list_filter = ('formato', 'genero', 'artista', 'activo', 'año_lanzamiento')
    search_fields = ('titulo', 'artista__nombre', 'descripcion')
    list_editable = ('precio', 'stock', 'activo')
    raw_id_fields = ('artista',)

@admin.register(CategoriaInstrumento)
class CategoriaInstrumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'descripcion')
    list_filter = ('tipo',)
    search_fields = ('nombre',)

class InstrumentoInline(admin.TabularInline):
    model = Instrumento
    extra = 0
    fields = ('nombre', 'marca', 'precio', 'stock', 'activo')

@admin.register(Instrumento)
class InstrumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'marca', 'categoria', 'precio', 'estado', 'stock', 'activo')
    list_filter = ('categoria', 'categoria__tipo', 'estado', 'activo', 'marca')
    search_fields = ('nombre', 'marca', 'modelo', 'descripcion')
    list_editable = ('precio', 'stock', 'activo')
    raw_id_fields = ('categoria',)

@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ciudad', 'activa', 'created_at')
    list_filter = ('activa', 'ciudad', 'created_at')
    search_fields = ('nombre', 'ciudad', 'direccion')
    list_editable = ('activa',)

@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'sucursal', 'stock_disponible', 'stock_reservado', 'stock_total')
    list_filter = ('sucursal', 'producto_disco', 'producto_instrumento')
    search_fields = ('producto_disco__titulo', 'producto_instrumento__nombre', 'sucursal__nombre')
    raw_id_fields = ('producto_disco', 'producto_instrumento', 'sucursal')
    
    def producto(self, obj):
        return obj.producto

@admin.register(InventarioMovimiento)
class InventarioMovimientoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'sucursal', 'tipo', 'cantidad', 'usuario', 'created_at')
    list_filter = ('tipo', 'sucursal', 'created_at', 'usuario')
    search_fields = ('producto_disco__titulo', 'producto_instrumento__nombre', 'motivo')
    raw_id_fields = ('producto_disco', 'producto_instrumento', 'sucursal', 'usuario')
    readonly_fields = ('created_at',)
    
    def producto(self, obj):
        return obj.producto

    
    def contenido_preview(self, obj):
        return obj.contenido[:50] + '...' if len(obj.contenido) > 50 else obj.contenido
    contenido_preview.short_description = 'Contenido'

admin.site.site_header = "A Destiempo - Administración"
admin.site.site_title = "A Destiempo Admin"
admin.site.index_title = "Panel de Administración"
