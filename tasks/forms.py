from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from PIL import Image
from .models import Disco, Instrumento, Artista, Genero, CategoriaInstrumento, Refaccion, CategoriaRefaccion, HeroBanner, CompatibilidadGeneral
import requests
import re
from datetime import datetime

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'username': 'Nombre de usuario',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

# Lista predefinida de géneros musicales
GENEROS_PREDEFINIDOS = [
    ('Rock', 'Rock'),
    ('Pop', 'Pop'),
    ('Jazz', 'Jazz'),
    ('Blues', 'Blues'),
    ('Clásica', 'Clásica'),
    ('Country', 'Country'),
    ('Rap/Hip-Hop', 'Rap/Hip-Hop'),
    ('R&B', 'R&B'),
    ('Reggae', 'Reggae'),
    ('Salsa', 'Salsa'),
    ('Cumbia', 'Cumbia'),
    ('Bachata', 'Bachata'),
    ('Merengue', 'Merengue'),
    ('Electronic', 'Electronic'),
    ('Metal', 'Metal'),
    ('Punk', 'Punk'),
    ('Folk', 'Folk'),
    ('Soul', 'Soul'),
    ('Funk', 'Funk'),
    ('Disco', 'Disco'),
    ('Alternative', 'Alternative'),
    ('Indie', 'Indie'),
    ('Latin', 'Latin'),
    ('World Music', 'World Music'),
    ('Gospel', 'Gospel'),
    ('Ópera', 'Ópera'),
    ('Bossa Nova', 'Bossa Nova'),
    ('Ska', 'Ska'),
    ('Reggaeton', 'Reggaeton'),
    ('Trap', 'Trap'),
]

def validar_artista_nombre(nombre):
    """Valida y corrige el nombre del artista usando API de MusicBrainz"""
    if not nombre or len(nombre.strip()) < 2:
        return nombre.strip()
    
    nombre_limpio = nombre.strip()
    
    # Corregir caracteres comunes
    correcciones = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N',
    }
    
    # Aplicar correcciones básicas
    nombre_corregido = ''.join(correcciones.get(c, c) for c in nombre_limpio)
    
    # Normalizar espacios múltiples
    nombre_corregido = re.sub(r'\s+', ' ', nombre_corregido)
    
    # Intentar buscar en MusicBrainz API (opcional, no bloquea si falla)
    try:
        url = f"https://musicbrainz.org/ws/2/artist/?query={nombre_corregido}&limit=1&fmt=json"
        headers = {'User-Agent': 'A Destiempo/1.0 (https://example.com)'}
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('artists') and len(data['artists']) > 0:
                artista_correcto = data['artists'][0].get('name', nombre_corregido)
                # Si el nombre encontrado es similar, usar el correcto
                if artista_correcto.lower().replace(' ', '') == nombre_corregido.lower().replace(' ', ''):
                    return artista_correcto
    except:
        pass  # Si falla la API, continuar con el nombre corregido manualmente
    
    return nombre_corregido

class ArtistaField(forms.ModelChoiceField):
    """Campo personalizado para artista con validación automática"""
    def __init__(self, *args, **kwargs):
        super().__init__(queryset=Artista.objects.all().order_by('nombre'), *args, **kwargs)
        self.widget.attrs.update({'class': 'form-select'})
    
    def clean(self, value):
        if value:
            # Si es un ID existente, retornar el artista
            return super().clean(value)
        return None


class HeroBannerForm(forms.ModelForm):
    class Meta:
        model = HeroBanner
        fields = [
            'imagen',
            'titulo',
            'subtitulo',
            'boton_1_texto',
            'boton_1_url',
            'boton_2_texto',
            'boton_2_url'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título principal del banner'}),
            'subtitulo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Texto descriptivo'}),
            'boton_1_texto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Texto botón principal'}),
            'boton_1_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL botón principal (opcional)'}),
            'boton_2_texto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Texto segundo botón'}),
            'boton_2_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL segundo botón (opcional)'}),
        }
        labels = {
            'imagen': 'Imagen del banner',
            'titulo': 'Título principal',
            'subtitulo': 'Subtítulo',
            'boton_1_texto': 'Texto del botón principal',
            'boton_1_url': 'Enlace del botón principal',
            'boton_2_texto': 'Texto del botón secundario',
            'boton_2_url': 'Enlace del botón secundario',
        }

    def clean(self):
        cleaned = super().clean()
        for key in ['boton_1_texto', 'boton_1_url', 'boton_2_texto', 'boton_2_url']:
            value = cleaned.get(key)
            if isinstance(value, str):
                cleaned[key] = value.strip()
        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['imagen'].widget.attrs.update({'class': 'form-control'})

class DiscoForm(forms.ModelForm):
    # Campo de artista (texto libre con autocomplete)
    artista_nombre = forms.CharField(
        max_length=100,
        required=False,  # Lo manejaremos en clean()
        label='Artista *',
        help_text='Escribe el nombre del artista. Si ya existe, aparecerán sugerencias.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: The Beatles',
            'id': 'id_artista_nombre',
            'list': 'artistas-list',
            'autocomplete': 'off'
        })
    )
    
    # Campo oculto para el artista_id (si se selecciona uno existente)
    artista_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'id_artista_id'})
    )
    
    # Stock para el formato seleccionado
    stock = forms.IntegerField(
        required=True,
        min_value=0,
        initial=0,
        label='Cantidad',
        help_text='Cantidad disponible para el formato seleccionado',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Disco
        fields = ['titulo', 'artista', 'genero', 'año_lanzamiento', 'formato', 'precio', 'descripcion', 'portada', 'activo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'artista': forms.HiddenInput(attrs={'required': False}),  # Campo oculto, se maneja con artista_nombre
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'año_lanzamiento': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1950,
                'max': datetime.now().year,
                'placeholder': f'1950 - {datetime.now().year}'
            }),
            'formato': forms.Select(attrs={'class': 'form-select'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'portada': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'id_portada'
            }),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer que el campo artista no sea requerido (lo manejaremos en clean())
        self.fields['artista'].required = False
        
        # Asegurar que solo se muestren géneros predefinidos
        # Crear géneros que no existan aún
        for genero_nombre, _ in GENEROS_PREDEFINIDOS:
            Genero.objects.get_or_create(nombre=genero_nombre, defaults={'nombre': genero_nombre})
        
        # Filtrar solo géneros predefinidos
        self.fields['genero'].queryset = Genero.objects.filter(
            nombre__in=[g[0] for g in GENEROS_PREDEFINIDOS]
        ).order_by('nombre')
        
        # Asegurar que el widget tenga la clase correcta
        self.fields['genero'].widget.attrs.update({'class': 'form-select'})
        
        # Agregar help text para géneros
        self.fields['genero'].help_text = 'Selecciona un género de la lista predefinida'
        
        # Si es edición, mostrar datos existentes
        if self.instance and self.instance.pk:
            # Mostrar nombre del artista actual
            if self.instance.artista:
                self.fields['artista_nombre'].initial = self.instance.artista.nombre
                self.fields['artista_id'].initial = self.instance.artista.id
                # Asignar artista al formulario para que no sea requerido
                self.initial['artista'] = self.instance.artista
                self.fields['artista'].initial = self.instance.artista
            
            # Mostrar stock actual para el formato del disco
            from .models import Inventario, Sucursal
            try:
                sucursal_principal = Sucursal.objects.get(nombre='Principal')
                try:
                    inventario = Inventario.objects.get(
                        producto_disco=self.instance,
                        formato_disco=self.instance.formato,
                        sucursal=sucursal_principal
                    )
                    self.fields['stock'].initial = inventario.stock_disponible
                except Inventario.DoesNotExist:
                    self.fields['stock'].initial = 0
            except Sucursal.DoesNotExist:
                self.fields['stock'].initial = 0
    
    def clean_portada(self):
        portada = self.cleaned_data.get('portada')
        if portada:
            # Validar que sea una imagen
            try:
                img = Image.open(portada)
                width, height = img.size
                
                # Validar tamaño mínimo (500x500 píxeles)
                if width < 500 or height < 500:
                    raise ValidationError(
                        f'La imagen debe tener al menos 500x500 píxeles. '
                        f'Tu imagen es {width}x{height} píxeles.'
                    )
                
                # Validar que sea cuadrada (tolerancia del 5%)
                aspect_ratio = width / height if height > 0 else 0
                if aspect_ratio < 0.95 or aspect_ratio > 1.05:
                    raise ValidationError(
                        f'La imagen debe ser cuadrada. '
                        f'Tu imagen es {width}x{height} píxeles (ratio: {aspect_ratio:.2f}).'
                    )
                
            except Exception as e:
                if isinstance(e, ValidationError):
                    raise
                raise ValidationError('El archivo no es una imagen válida.')
        
        return portada
    
    def clean_artista_nombre(self):
        artista_nombre = self.cleaned_data.get('artista_nombre', '').strip()
        if not artista_nombre:
            raise ValidationError('El nombre del artista es requerido.')
        
        # Validar y corregir nombre del artista
        nombre_corregido = validar_artista_nombre(artista_nombre)
        return nombre_corregido
    
    def clean(self):
        cleaned_data = super().clean()
        artista_nombre = cleaned_data.get('artista_nombre', '').strip() or ''
        artista_id = cleaned_data.get('artista_id')
        
        # Si es edición y ya tiene artista, usar ese artista
        if self.instance and self.instance.pk and self.instance.artista:
            if not artista_nombre:
                artista_nombre = self.instance.artista.nombre
                cleaned_data['artista_nombre'] = artista_nombre
            # Si ya tiene artista, usarlo directamente
            if not artista_id:
                artista = self.instance.artista
                cleaned_data['artista'] = artista
                return cleaned_data
        
        # Validar que haya artista_nombre o artista_id
        if not artista_nombre and not artista_id:
            raise ValidationError({'artista_nombre': 'El nombre del artista es requerido.'})
        
        # Si hay un artista_id seleccionado, usarlo
        if artista_id:
            try:
                artista = Artista.objects.get(id=artista_id)
                # Si hay nombre y no coincide, usar el nombre del campo
                if artista_nombre and artista.nombre.lower() != artista_nombre.lower():
                    artista, created = Artista.objects.get_or_create(
                        nombre=artista_nombre,
                        defaults={'nombre': artista_nombre}
                    )
            except Artista.DoesNotExist:
                # Si el ID no existe, crear/obtener por nombre
                if artista_nombre:
                    artista, created = Artista.objects.get_or_create(
                        nombre=artista_nombre,
                        defaults={'nombre': artista_nombre}
                    )
                else:
                    raise ValidationError({'artista_nombre': 'El nombre del artista es requerido.'})
        else:
            # Si no hay ID, buscar por nombre o crear
            if artista_nombre:
                artista, created = Artista.objects.get_or_create(
                    nombre=artista_nombre,
                    defaults={'nombre': artista_nombre}
                )
            else:
                raise ValidationError({'artista_nombre': 'El nombre del artista es requerido.'})
        
        # Asegurar que el artista esté en cleaned_data
        cleaned_data['artista'] = artista
        
        return cleaned_data
    
    def save(self, commit=True):
        # Obtener el artista de cleaned_data
        artista = self.cleaned_data.get('artista')
        
        # Asignar el artista al disco ANTES de llamar a super().save()
        if artista:
            self.instance.artista = artista
        
        disco = super().save(commit=False)
        
        # Verificación final: asegurar que el artista esté asignado
        if not disco.artista:
            if artista:
                disco.artista = artista
            else:
                # Si aún no hay artista, obtenerlo del nombre
                artista_nombre = self.cleaned_data.get('artista_nombre', '').strip()
                if artista_nombre:
                    artista, created = Artista.objects.get_or_create(
                        nombre=artista_nombre,
                        defaults={'nombre': artista_nombre}
                    )
                    disco.artista = artista
        
        if commit:
            disco.save()
            
            # Guardar stock para el formato seleccionado
            from .models import Inventario, Sucursal
            try:
                sucursal_principal = Sucursal.objects.get(nombre='Principal')
            except Sucursal.DoesNotExist:
                sucursal_principal = Sucursal.objects.create(nombre='Principal', activa=True)
            
            # Obtener el formato del disco
            formato = disco.formato
            stock = self.cleaned_data.get('stock', 0) or 0
            
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
        
        return disco

class InstrumentoForm(forms.ModelForm):
    class Meta:
        model = Instrumento
        fields = ['nombre', 'marca', 'categoria', 'modelo', 'precio', 'estado', 'descripcion', 'imagen_principal', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'imagen_principal': forms.FileInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class RefaccionForm(forms.ModelForm):
    class Meta:
        model = Refaccion
        fields = ['nombre', 'marca', 'categoria', 'compatibilidad_general', 'modelo_compatible', 'precio', 'stock', 'descripcion', 'imagen_principal', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'compatibilidad_general': forms.Select(attrs={'class': 'form-select'}),
            'modelo_compatible': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'imagen_principal': forms.FileInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar que existan categorías generales de compatibilidad por defecto
        categorias_compat = [
            'Guitarra Eléctrica',
            'Guitarra Acústica',
            'Bajo Eléctrico',
            'Batería / Percusión',
            'Teclado / Piano',
            'Audio (Cables, Conectividad)',
            'Sistemas Inalámbricos',
            'Micrófonos',
            'DJ / Controladores',
            'Estuches / Fundas',
            'Accesorios Universales',
        ]
        for nombre in categorias_compat:
            CompatibilidadGeneral.objects.get_or_create(nombre=nombre, defaults={'nombre': nombre})
        self.fields['compatibilidad_general'].queryset = CompatibilidadGeneral.objects.all().order_by('nombre')
