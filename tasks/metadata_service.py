"""
Servicio para buscar metadatos de discos en internet
Usa MusicBrainz API y otras fuentes
"""
import requests
import re
from typing import Dict, List, Optional
from urllib.parse import quote, urlparse, unquote
import os
import concurrent.futures
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageOps


def es_url_wikimedia(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return 'wikimedia.org' in parsed.netloc.lower()
    except Exception:
        return False


def construir_url_wikimedia_alta_res(url: str, width: int = 1920) -> Optional[str]:
    """Construye una URL alternativa para Wikimedia con ancho especificado."""
    if not es_url_wikimedia(url):
        return None
    try:
        parsed = urlparse(url)
        filename = parsed.path.split('/')[-1]
        if not filename:
            return None
        return f"https://commons.wikimedia.org/wiki/Special:FilePath/{quote(filename)}?width={width}"
    except Exception:
        return None


def construir_referer_wikimedia(url: str) -> str:
    if not es_url_wikimedia(url):
        return 'https://musicbrainz.org/'
    try:
        parsed = urlparse(url)
        parts = parsed.path.split('/')
        if 'Special:FilePath' in parts:
            filename = parts[-1]
        else:
            filename = parts[-1]
        filename = unquote(filename)
        if not filename:
            return 'https://commons.wikimedia.org/'
        return f"https://commons.wikimedia.org/wiki/File:{quote(filename)}"
    except Exception:
        return 'https://commons.wikimedia.org/'


def es_url_lastfm(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return 'lastfm.freetls.fastly.net' in parsed.netloc.lower()
    except Exception:
        return False


def generar_variantes_lastfm(url: str) -> List[str]:
    if not es_url_lastfm(url):
        return [url]
    pattern = r'/i/u/([^/]+)/'
    if not re.search(pattern, url):
        return [url]
    sizes = ['2048x2048', '1280x1280', '1000x1000', '770x0', '640x640', '500x500', '300x300']
    variantes = []
    for size in sizes:
        variantes.append(re.sub(pattern, f'/i/u/{size}/', url, count=1))
    # Asegurar que la original esté al final por si no coincide con ninguna variante
    if url not in variantes:
        variantes.append(url)
    return variantes


def obtener_imagen_lastfm(artista_nombre: str, headers: dict, timeout: float = 5.0) -> Optional[str]:
    """Obtiene imagen del artista usando Last.fm (requiere API key)."""
    api_key = getattr(settings, 'LASTFM_API_KEY', '').strip()
    if not api_key:
        return None
    
    lang = getattr(settings, 'LASTFM_API_LANG', 'en')
    url = (
        f"https://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={quote(artista_nombre)}"
        f"&api_key={api_key}&format=json&lang={lang}"
    )
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code != 200:
            print(f"Last.fm respondió {response.status_code} para {artista_nombre}")
            return None
        
        data = response.json()
        artist_info = data.get('artist')
        if not artist_info:
            return None
        
        images = artist_info.get('image', [])
        if not images:
            return None
        
        size_priority = ['mega', 'extralarge', 'large', 'medium', 'small']
        best_url = None
        best_priority = len(size_priority)
        
        for img in images:
            url_img = img.get('#text')
            size = img.get('size', '')
            if not url_img:
                continue
            if size in size_priority:
                priority = size_priority.index(size)
            else:
                priority = len(size_priority) - 1
            if priority < best_priority:
                best_priority = priority
                best_url = url_img
        
        if best_url:
            size_label = size_priority[best_priority] if best_priority < len(size_priority) else 'desconocido'
            print(f"Imagen encontrada en Last.fm ({size_label}) para {artista_nombre}")
        return best_url
    except Exception as e:
        print(f"Error buscando imagen en Last.fm para {artista_nombre}: {e}")
        return None

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

def descargar_portada(url: str, disco_titulo: str, artista_nombre: str) -> Optional[ContentFile]:
    """
    Descarga una portada desde una URL y la devuelve como ContentFile para asignar a ImageField
    
    Args:
        url: URL de la imagen
        disco_titulo: Título del disco (para nombrar el archivo)
        artista_nombre: Nombre del artista (para la ruta)
    
    Returns:
        ContentFile con la imagen o None si falla
    """
    try:
        response = requests.get(url, timeout=10, stream=True)
        response.raise_for_status()
        
        # Verificar que sea una imagen
        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type:
            print(f"El contenido no es una imagen: {content_type}")
            return None
        
        # Leer contenido de la imagen
        image_content = response.content
        
        # Procesar imagen para asegurar calidad (mínimo 300x300, preferiblemente cuadrada)
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(image_content))
            width, height = img.size
            original_format = img.format
            
            print(f"Imagen original: {width}x{height}, formato: {original_format}")
            
            # Si la imagen es muy pequeña (menos de 300x300), redimensionar
            min_size = 300  # Reducido de 500 a 300 para ser más tolerante
            if width < min_size or height < min_size:
                # Redimensionar manteniendo aspecto
                if width < height:
                    new_width = min_size
                    new_height = int(height * (min_size / width))
                else:
                    new_height = min_size
                    new_width = int(width * (min_size / height))
                
                print(f"Redimensionando a: {new_width}x{new_height}")
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                width, height = new_width, new_height
            
            # Si no es cuadrada, recortar al centro (con tolerancia del 10%)
            aspect_ratio = width / height if height > 0 else 1
            if abs(aspect_ratio - 1.0) > 0.10:  # 10% de tolerancia (más permisivo)
                size = min(width, height)
                left = (width - size) // 2
                top = (height - size) // 2
                print(f"Recortando a cuadrado: {size}x{size} desde ({left}, {top})")
                img = img.crop((left, top, left + size, top + size))
            
            # Convertir a JPEG para consistencia
            output = io.BytesIO()
            # Si la imagen tiene transparencia, convertir a RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (0, 0, 0))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            img.save(output, format='JPEG', quality=90)
            image_content = output.getvalue()
            print(f"Imagen procesada: {len(image_content)} bytes")
        except Exception as e:
            print(f"Error al procesar imagen: {e}")
            import traceback
            traceback.print_exc()
            # Continuar con la imagen original si falla el procesamiento
            print("Usando imagen original sin procesar")
        
        # Generar nombre de archivo seguro
        safe_titulo = re.sub(r'[^\w\s-]', '', disco_titulo).strip()[:50]
        safe_artista = re.sub(r'[^\w\s-]', '', artista_nombre).strip()[:50]
        safe_titulo = re.sub(r'[-\s]+', '-', safe_titulo)
        safe_artista = re.sub(r'[-\s]+', '-', safe_artista)
        
        # Obtener extensión de la URL o usar JPEG por defecto
        ext = '.jpg'
        if '.png' in url.lower():
            ext = '.png'
        elif '.webp' in url.lower():
            ext = '.webp'
        
        filename = f"{safe_titulo}_{safe_artista}{ext}"
        
        # Devolver ContentFile para asignar directamente al ImageField
        file = ContentFile(image_content, name=filename)
        print(f"Portada descargada y preparada: {filename} ({len(image_content)} bytes)")
        return file
        
    except Exception as e:
        print(f"Error al descargar portada: {e}")
        import traceback
        traceback.print_exc()
        return None

def obtener_imagen_artista(artista_nombre: str, timeout: float = 5.0) -> Optional[str]:
    """
    Obtiene la URL de la imagen de un artista desde múltiples fuentes.
    
    Fuentes intentadas (en orden de prioridad):
    1. Overrides configurados en settings (ARTIST_IMAGE_OVERRIDES)
    2. MusicBrainz + fanart.tv (requiere MBID)
    3. Last.fm API (recomendado, requiere API key)
    4. Wikipedia (API REST)
    
    Args:
        artista_nombre: Nombre del artista
        timeout: Timeout para la petición
    
    Returns:
        URL de la imagen del artista o None si no se encuentra
    """
    # Paso 0: Revisar overrides configurados manualmente
    overrides_config = getattr(settings, 'ARTIST_IMAGE_OVERRIDES', {})
    override_value = overrides_config.get(artista_nombre)
    if override_value:
        if isinstance(override_value, (list, tuple)):
            for item in override_value:
                if item:
                    print(f"Override manual encontrado para {artista_nombre}: {item}")
                    return item
        elif isinstance(override_value, str) and override_value.strip():
            print(f"Override manual encontrado para {artista_nombre}: {override_value}")
            return override_value.strip()
    
    headers = {
        'User-Agent': 'A Destiempo/1.0 (https://example.com)',
        'Accept': 'application/json'
    }
    
    mbid = None
    
    # Paso 1: Buscar artista en MusicBrainz para obtener MBID
    try:
        mb_url = f"https://musicbrainz.org/ws/2/artist/?query=artist:{quote(artista_nombre)}&limit=1&fmt=json"
        mb_response = requests.get(mb_url, headers=headers, timeout=timeout)
        
        if mb_response.status_code == 200:
            mb_data = mb_response.json()
            artists = mb_data.get('artists', [])
            if artists:
                artist = artists[0]
                mbid = artist.get('id', '')
                print(f"MBID encontrado para {artista_nombre}: {mbid}")
    except Exception as e:
        print(f"Error buscando en MusicBrainz: {e}")
    
    # Paso 2: Intentar obtener imagen desde fanart.tv usando MBID
    if mbid:
        try:
            # fanart.tv requiere API key, pero podemos intentar sin ella (a veces funciona)
            # También podemos usar la clave demo que a veces funciona
            fanart_url = f"https://webservice.fanart.tv/v3/music/{mbid}"
            fanart_headers = {
                **headers,
                'api-key': 'demo'  # Clave demo, puede que no funcione siempre
            }
            
            fanart_response = requests.get(fanart_url, headers=fanart_headers, timeout=timeout)
            
            if fanart_response.status_code == 200:
                fanart_data = fanart_response.json()
                
                # Priorizar artistbackground (fondos grandes)
                artistbackground = fanart_data.get('artistbackground', [])
                if artistbackground and len(artistbackground) > 0:
                    # Ordenar por ancho, mayor primero
                    artistbackground.sort(key=lambda x: x.get('width', 0), reverse=True)
                    url = artistbackground[0].get('url', '')
                    if url:
                        print(f"Imagen encontrada en fanart.tv (background) para {artista_nombre}")
                        return url
                
                # Si no hay background, intentar con artistthumb
                artistthumb = fanart_data.get('artistthumb', [])
                if artistthumb and len(artistthumb) > 0:
                    artistthumb.sort(key=lambda x: x.get('width', 0), reverse=True)
                    url = artistthumb[0].get('url', '')
                    if url:
                        print(f"Imagen encontrada en fanart.tv (thumb) para {artista_nombre}")
                        return url
        except Exception as e:
            print(f"Error obteniendo imagen desde fanart.tv: {e}")
    
    # Paso 3: Intentar con Last.fm (con API key si está configurada)
    imagen_lastfm = obtener_imagen_lastfm(artista_nombre, headers=headers, timeout=timeout)
    if imagen_lastfm:
        return imagen_lastfm
    
    # Fallback muy básico de Last.fm sin API key (si no se configuró)
    if not getattr(settings, 'LASTFM_API_KEY', '').strip():
        try:
            lastfm_search_url = f"https://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={quote(artista_nombre)}&format=json"
            lastfm_response = requests.get(lastfm_search_url, headers=headers, timeout=timeout)
            
            if lastfm_response.status_code == 200:
                lastfm_data = lastfm_response.json()
                artist_info = lastfm_data.get('artist', {})
                if artist_info:
                    images = artist_info.get('image', [])
                    if images and len(images) > 0:
                        for size in ['extralarge', 'large', 'medium']:
                            for img in images:
                                if img.get('size') == size:
                                    url = img.get('#text', '')
                                    if url and url.strip():
                                        print(f"Imagen encontrada en Last.fm (sin API key, {size}) para {artista_nombre}")
                                        return url
        except Exception as e:
            print(f"Error buscando en Last.fm (sin API key): {e}")
    
    # Paso 4: Intentar obtener imagen desde Wikipedia (REST API)
    wikipedia_titles = []
    wikipedia_overrides = getattr(settings, 'ARTIST_WIKIPEDIA_TITLES', {})
    override_titles = wikipedia_overrides.get(artista_nombre)
    if override_titles:
        if isinstance(override_titles, (list, tuple)):
            wikipedia_titles.extend([title for title in override_titles if title])
        elif isinstance(override_titles, str):
            wikipedia_titles.append(override_titles)
    
    # Variaciones por defecto
    normalized = artista_nombre.replace(' ', '_')
    wikipedia_titles.extend([
        normalized,
        f"{normalized}_band",
        f"{normalized}_group",
        f"{normalized}_(band)",
        f"{normalized}_(group)",
        artista_nombre
    ])
    
    wikipedia_titles = list(dict.fromkeys([title for title in wikipedia_titles if title]))
    wikipedia_languages = getattr(settings, 'ARTIST_WIKIPEDIA_LANGUAGES', ['en', 'es', 'de'])
    
    for title in wikipedia_titles:
        for language in wikipedia_languages:
            try:
                wiki_url = f"https://{language}.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
                wiki_headers = {
                    'User-Agent': headers['User-Agent'],
                    'Accept': 'application/json'
                }
                response = requests.get(wiki_url, headers=wiki_headers, timeout=timeout)
                if response.status_code == 200:
                    data = response.json()
                    original = data.get('originalimage', {})
                    thumbnail = data.get('thumbnail', {})
                    wiki_image_url = original.get('source') or thumbnail.get('source')
                    if wiki_image_url:
                        print(f"Imagen encontrada en Wikipedia ({language}) para {artista_nombre}")
                        return wiki_image_url
            except Exception as e:
                print(f"Error buscando imagen en Wikipedia ({language}/{title}): {e}")
    
    print(f"No se encontró imagen del artista para {artista_nombre}")
    return None

def descargar_imagen_artista(url: str, artista_nombre: str) -> Optional[ContentFile]:
    """
    Descarga una imagen de artista desde una URL y la devuelve como ContentFile
    
    Args:
        url: URL de la imagen
        artista_nombre: Nombre del artista (para nombrar el archivo)
    
    Returns:
        ContentFile con la imagen o None si falla
    """
    # Configuración dinámica
    min_width = getattr(settings, 'ARTIST_IMAGE_MIN_WIDTH', 1600)
    min_height = getattr(settings, 'ARTIST_IMAGE_MIN_HEIGHT', 900)
    target_size = getattr(settings, 'ARTIST_IMAGE_TARGET_SIZE', (1920, 1080))
    
    try:
        urls_por_probar: List[str] = []
        
        if es_url_lastfm(url):
            urls_por_probar.extend(generar_variantes_lastfm(url))
        else:
            urls_por_probar.append(url)
        
        if es_url_wikimedia(url):
            alta_res_url = construir_url_wikimedia_alta_res(url, max(min_width, target_size[0]))
            if alta_res_url:
                urls_por_probar.insert(0, alta_res_url)
            if url not in urls_por_probar:
                urls_por_probar.append(url)
        
        vistos = set()
        
        for download_url in urls_por_probar:
            if download_url in vistos:
                continue
            vistos.add(download_url)
            
            download_headers = {
                'User-Agent': 'A-DestiempoBot/1.0 (+https://adestiempo.local/; contact=dev@adestiempo.com)',
                'Accept': 'image/*,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Referer': construir_referer_wikimedia(download_url) if es_url_wikimedia(download_url) else 'https://musicbrainz.org/'
            }
            
            try:
                response = requests.get(download_url, timeout=10, stream=True, headers=download_headers)
                response.raise_for_status()
            except Exception as e:
                print(f"Error descargando {download_url}: {e}")
                continue
            
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type:
                print(f"El contenido no es una imagen ({content_type}) para {download_url}")
                continue
            
            image_content = response.content
            
            try:
                import io
                img = Image.open(io.BytesIO(image_content))
                width, height = img.size
                
                if width < min_width or height < min_height:
                    print(f"Imagen {width}x{height} demasiado pequeña para {artista_nombre}: {download_url}")
                    continue
                
                img = img.convert('RGB') if img.mode in ('RGBA', 'LA', 'P') else img
                img = ImageOps.fit(
                    img,
                    target_size,
                    method=Image.Resampling.LANCZOS,
                    centering=(0.5, 0.5)
                )
                
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=90, optimize=True)
                image_content = output.getvalue()
                
                safe_artista = re.sub(r'[^\w\s-]', '', artista_nombre).strip()[:50]
                safe_artista = re.sub(r'[-\s]+', '-', safe_artista)
                filename = f"{safe_artista}.jpg"
                
                file = ContentFile(image_content, name=filename)
                print(f"Imagen de artista descargada: {filename} ({len(image_content)} bytes) desde {download_url}")
                return file
            except Exception as e:
                print(f"Error al procesar imagen de artista desde {download_url}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"No se encontró imagen con la calidad mínima para {artista_nombre}")
        return None
        
    except Exception as e:
        print(f"Error al descargar imagen de artista: {e}")
        import traceback
        traceback.print_exc()
        return None

def obtener_o_descargar_imagen_artista(artista, forzar_redescarga=False):
    """
    Obtiene o descarga la imagen de un artista si no existe
    
    Args:
        artista: Instancia del modelo Artista
        forzar_redescarga: Si es True, descarga la imagen incluso si ya existe
    
    Returns:
        True si se obtuvo/descargó la imagen, False en caso contrario
    """
    # Si ya tiene imagen y no se fuerza la re-descarga, no hacer nada
    if artista.foto and not forzar_redescarga:
        print(f"El artista {artista.nombre} ya tiene imagen. Usa forzar_redescarga=True para re-descargarla")
        return True
    
    # Si se fuerza la re-descarga, eliminar la imagen existente
    if artista.foto and forzar_redescarga:
        try:
            # Eliminar el archivo físico
            if artista.foto.storage.exists(artista.foto.name):
                artista.foto.delete(save=False)
            print(f"Imagen anterior eliminada para {artista.nombre}, descargando nueva...")
        except Exception as e:
            print(f"Error al eliminar imagen anterior: {e}")
    
    print(f"Buscando imagen para {artista.nombre}...")
    
    # Intentar obtener imagen desde API
    imagen_url = obtener_imagen_artista(artista.nombre)
    
    if imagen_url:
        print(f"URL de imagen encontrada: {imagen_url}")
        # Descargar y guardar la imagen
        imagen_file = descargar_imagen_artista(imagen_url, artista.nombre)
        if imagen_file:
            try:
                # Guardar la imagen en el modelo
                artista.foto.save(imagen_file.name, imagen_file, save=True)
                print(f"Imagen guardada exitosamente para {artista.nombre}: {artista.foto.name}")
                return True
            except Exception as e:
                print(f"Error al guardar imagen: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print(f"No se pudo descargar la imagen desde {imagen_url}")
    else:
        print(f"No se encontró imagen para {artista.nombre}")
    
    return False

