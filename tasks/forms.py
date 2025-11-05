from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from PIL import Image
from .models import Disco, Instrumento, Artista, Genero, CategoriaInstrumento
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

class DiscoForm(forms.ModelForm):
    # Campo para crear nuevo artista
    nuevo_artista = forms.CharField(
        max_length=100,
        required=False,
        label='Nuevo Artista (si no existe)',
        help_text='Ingresa el nombre del artista. Se validará y corregirá automáticamente.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: The Beatles',
            'id': 'id_nuevo_artista'
        })
    )
    
    # Stock por formato
    stock_vinilo = forms.IntegerField(
        required=False,
        min_value=0,
        initial=0,
        label='Stock Vinilo',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    stock_cd = forms.IntegerField(
        required=False,
        min_value=0,
        initial=0,
        label='Stock CD',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    stock_digital = forms.IntegerField(
        required=False,
        min_value=0,
        initial=0,
        label='Stock Digital',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    stock_casete = forms.IntegerField(
        required=False,
        min_value=0,
        initial=0,
        label='Stock Casete',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Disco
        fields = ['titulo', 'artista', 'genero', 'año_lanzamiento', 'formato', 'precio', 'descripcion', 'portada', 'activo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'artista': forms.Select(attrs={'class': 'form-select', 'id': 'id_artista'}),
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
        # Asegurar que solo se muestren géneros predefinidos
        self.fields['genero'].queryset = Genero.objects.filter(
            nombre__in=[g[0] for g in GENEROS_PREDEFINIDOS]
        ).order_by('nombre')
        # Asegurar que el widget tenga la clase correcta
        self.fields['genero'].widget.attrs.update({'class': 'form-select'})
        
        # Si es edición, mostrar stock actual por formato
        if self.instance and self.instance.pk:
            from .models import Inventario, Sucursal
            try:
                sucursal_principal = Sucursal.objects.get(nombre='Principal')
                for formato in ['vinilo', 'cd', 'digital', 'casete']:
                    try:
                        inventario = Inventario.objects.get(
                            producto_disco=self.instance,
                            formato_disco=formato,
                            sucursal=sucursal_principal
                        )
                        self.fields[f'stock_{formato}'].initial = inventario.stock_disponible
                    except Inventario.DoesNotExist:
                        pass
            except Sucursal.DoesNotExist:
                pass
    
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
    
    def clean_nuevo_artista(self):
        nuevo_artista = self.cleaned_data.get('nuevo_artista')
        if nuevo_artista:
            # Validar y corregir nombre del artista
            nombre_corregido = validar_artista_nombre(nuevo_artista)
            return nombre_corregido
        return nuevo_artista
    
    def clean(self):
        cleaned_data = super().clean()
        artista = cleaned_data.get('artista')
        nuevo_artista = cleaned_data.get('nuevo_artista')
        
        # Si se proporciona un nuevo artista, crear o actualizar
        if nuevo_artista and not artista:
            nombre_corregido = self.clean_nuevo_artista()
            artista, created = Artista.objects.get_or_create(
                nombre=nombre_corregido,
                defaults={'nombre': nombre_corregido}
            )
            cleaned_data['artista'] = artista
        
        return cleaned_data
    
    def save(self, commit=True):
        disco = super().save(commit=False)
        
        if commit:
            disco.save()
            
            # Guardar stock por formato
            from .models import Inventario, Sucursal
            try:
                sucursal_principal = Sucursal.objects.get(nombre='Principal')
            except Sucursal.DoesNotExist:
                sucursal_principal = Sucursal.objects.create(nombre='Principal', activa=True)
            
            for formato in ['vinilo', 'cd', 'digital', 'casete']:
                stock = self.cleaned_data.get(f'stock_{formato}', 0) or 0
                if stock > 0:
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
