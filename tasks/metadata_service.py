"""
Servicio para buscar metadatos de discos en internet
Usa MusicBrainz API y otras fuentes
"""
import requests
import re
from typing import Dict, List, Optional
from urllib.parse import quote
import os
import concurrent.futures
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def obtener_portada_rapida(release_id: str, timeout: float = 1.0) -> Optional[str]:
    """Obtiene portada de forma rápida desde Cover Art Archive"""
    if not release_id:
        return None
    
    try:
        # Intentar directamente con la URL de 500px (más rápido y directo)
        cover_url_500 = f"https://coverartarchive.org/release/{release_id}/front-500"
        try:
            response = requests.head(cover_url_500, timeout=timeout, allow_redirects=True)
            if response.status_code in (200, 302, 301):
                return cover_url_500
        except:
            pass
        
        # Si falla, intentar con 250px (más rápido de cargar)
        cover_url_250 = f"https://coverartarchive.org/release/{release_id}/front-250"
        try:
            response = requests.head(cover_url_250, timeout=timeout, allow_redirects=True)
            if response.status_code in (200, 302, 301):
                return cover_url_250
        except:
            pass
        
        # Último intento rápido: endpoint JSON (solo si los anteriores fallan)
        try:
            cover_url = f"https://coverartarchive.org/release/{release_id}"
            response = requests.get(cover_url, timeout=timeout)
            if response.status_code == 200:
                cover_data = response.json()
                images = cover_data.get('images', [])
                if images:
                    # Buscar imagen frontal
                    front_image = next((img for img in images if img.get('front', False)), None)
                    if front_image:
                        return front_image.get('image', '')
                    elif images:
                        # Si no hay frontal, usar la primera imagen grande
                        return images[0].get('image', '')
        except:
            pass
    except Exception as e:
        print(f"Error obteniendo portada para {release_id}: {e}")
    
    return None

def obtener_info_version(release_id: str, release_group_id: str, headers: dict, release_title: str, release_tags: list = None, timeout: float = 0.5) -> Dict:
    """Obtiene información sobre versión del disco (deluxe, remastered, etc.) - versión ultra optimizada"""
    version_info = {
        'version': '',
        'tags': [],
        'disambiguation': ''
    }
    
    try:
        # Detectar versiones directamente del título (muy rápido, sin API calls)
        title_lower = release_title.lower()
        
        version_keywords = {
            'deluxe': ['deluxe', 'deluxe edition'],
            'remastered': ['remastered', 'remaster'],
            'anniversary': ['anniversary', 'anniversary edition'],
            'limited': ['limited edition', 'limited'],
            'special': ['special edition', 'special'],
            'expanded': ['expanded edition', 'expanded'],
            'bonus': ['bonus tracks', 'bonus edition'],
        }
        
        for version_type, keywords in version_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                version_info['version'] = version_type.capitalize()
                break
        
        # Usar tags del release original (si están disponibles) en lugar de hacer otra llamada
        if release_tags:
            version_info['tags'] = [tag.get('name', '') for tag in release_tags if tag.get('count', 0) > 0][:5]
    except:
        pass
    
    return version_info

def buscar_metadatos_disco(titulo: str, artista: Optional[str] = None) -> List[Dict]:
    """
    Busca metadatos de discos usando MusicBrainz API (optimizado)
    
    Args:
        titulo: Título del disco
        artista: Nombre del artista (opcional)
    
    Returns:
        Lista de diccionarios con metadatos encontrados
    """
    results = []
    
    try:
        # Construir query para MusicBrainz con más información incluida
        query_parts = [f'release:"{titulo}"']
        if artista:
            query_parts.append(f'artist:"{artista}"')
        
        query = ' AND '.join(query_parts)
        url = f"https://musicbrainz.org/ws/2/release/?query={quote(query)}&limit=10&inc=release-groups+tags&fmt=json"
        
        headers = {
            'User-Agent': 'A Destiempo/1.0 (https://example.com)',
            'Accept': 'application/json'
        }
        
        # Búsqueda principal con timeout corto
        response = requests.get(url, headers=headers, timeout=2)
        
        if response.status_code == 200:
            data = response.json()
            releases = data.get('releases', [])
            
            # Procesar releases en paralelo para obtener portadas
            def procesar_release(release):
                try:
                    release_title = release.get('title', '')
                    release_date = release.get('date', '')
                    release_id = release.get('id', '')
                    release_group = release.get('release-group', {})
                    release_group_id = release_group.get('id', '') if release_group else ''
                    
                    # Extraer artistas
                    artist_credits = release.get('artist-credit', [])
                    artists = []
                    if artist_credits:
                        for credit in artist_credits:
                            if isinstance(credit, dict):
                                artist_name = credit.get('name', '')
                                if artist_name:
                                    artists.append(artist_name)
                    
                    # Extraer géneros y tags (del release original)
                    tags = release.get('tags', [])
                    genres = [tag.get('name', '') for tag in tags if tag.get('count', 0) > 0]
                    
                    # Extraer año
                    year = None
                    if release_date:
                        year_match = re.search(r'(\d{4})', release_date)
                        if year_match:
                            year = int(year_match.group(1))
                    
                    # Obtener información de versión (ultra rápido, solo del título y tags disponibles, sin API calls)
                    version_info = obtener_info_version(release_id, release_group_id, headers, release_title, tags, timeout=0.3)
                    
                    # Obtener portada (ultra rápido: usar URL directa sin verificar)
                    # El navegador manejará errores 404 automáticamente
                    cover_art_url = f"https://coverartarchive.org/release/{release_id}/front-500" if release_id else None
                    
                    # Construir título completo con versión
                    titulo_completo = release_title
                    if version_info.get('version'):
                        titulo_completo += f" ({version_info['version']} Edition)"
                    elif version_info.get('disambiguation'):
                        titulo_completo += f" ({version_info['disambiguation']})"
                    
                    return {
                        'titulo': release_title,
                        'titulo_completo': titulo_completo,
                        'artista': ', '.join(artists) if artists else artista or 'Desconocido',
                        'artistas_lista': artists,
                        'año': year,
                        'fecha': release_date,
                        'generos': genres[:3] if genres else [],
                        'cover_art_url': cover_art_url,
                        'musicbrainz_id': release_id,
                        'version': version_info.get('version', ''),
                        'edicion': version_info.get('disambiguation', ''),
                        'tags': version_info.get('tags', [])[:5],
                    }
                except Exception as e:
                    print(f"Error procesando release: {e}")
                    return None
            
            # Procesar releases de forma rápida y simple (sin paralelismo para evitar timeouts)
            # Limitar a 6 releases máximo para velocidad
            for release in releases[:6]:
                try:
                    result = procesar_release(release)
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"Error procesando release: {e}")
                    continue
        
    except Exception as e:
        print(f"Error al buscar metadatos: {e}")
    
    # Ordenar resultados por año (más recientes primero) y luego por presencia de portada
    results.sort(key=lambda x: (
        x.get('cover_art_url') is None,  # Los con portada primero
        -(x.get('año') or 0)  # Más recientes primero
    ))
    
    return results

def descargar_portada(url: str, disco_titulo: str, artista_nombre: str) -> Optional[str]:
    """
    Descarga una portada desde una URL y la guarda en el sistema de archivos
    
    Args:
        url: URL de la imagen
        disco_titulo: Título del disco (para nombrar el archivo)
        artista_nombre: Nombre del artista (para la ruta)
    
    Returns:
        Ruta relativa del archivo guardado o None si falla
    """
    try:
        response = requests.get(url, timeout=10, stream=True)
        response.raise_for_status()
        
        # Verificar que sea una imagen
        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type:
            return None
        
        # Generar nombre de archivo seguro
        safe_titulo = re.sub(r'[^\w\s-]', '', disco_titulo).strip()[:50]
        safe_artista = re.sub(r'[^\w\s-]', '', artista_nombre).strip()[:50]
        safe_titulo = re.sub(r'[-\s]+', '-', safe_titulo)
        safe_artista = re.sub(r'[-\s]+', '-', safe_artista)
        
        # Obtener extensión de la URL
        ext = '.jpg'
        if '.png' in url.lower():
            ext = '.png'
        elif '.webp' in url.lower():
            ext = '.webp'
        
        filename = f"{safe_titulo}_{safe_artista}{ext}"
        
        # Crear ruta de destino
        media_path = os.path.join('discos', safe_artista, filename)
        
        # Leer contenido de la imagen
        image_content = response.content
        
        # Verificar que sea una imagen válida (mínimo 500x500)
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(image_content))
            width, height = img.size
            
            # Si no es cuadrada o es muy pequeña, intentar recortar/redimensionar
            if width < 500 or height < 500:
                # Redimensionar manteniendo aspecto
                if width < height:
                    new_width = 500
                    new_height = int(height * (500 / width))
                else:
                    new_height = 500
                    new_width = int(width * (500 / height))
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Si no es cuadrada, recortar al centro
                if abs(width - height) > width * 0.05:  # 5% de tolerancia
                    size = min(new_width, new_height)
                    left = (new_width - size) // 2
                    top = (new_height - size) // 2
                    img = img.crop((left, top, left + size, top + size))
                
                # Convertir a bytes
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=95)
                image_content = output.getvalue()
        except Exception as e:
            print(f"Error al procesar imagen: {e}")
            # Continuar con la imagen original si falla el procesamiento
        
        # Guardar archivo
        file = ContentFile(image_content)
        saved_path = default_storage.save(media_path, file)
        
        return saved_path
        
    except Exception as e:
        print(f"Error al descargar portada: {e}")
        return None

