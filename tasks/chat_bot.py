"""
Bot inteligente de chat para A Destiempo
Puede buscar productos, verificar disponibilidad y describir productos
"""
import re
from django.db.models import Q
from .models import Disco, Instrumento, Refaccion, Artista, CategoriaInstrumento


class ChatBot:
    """Bot inteligente que conoce el catálogo y puede responder preguntas"""
    
    def __init__(self):
        self.respuestas_generales = {
            'saludo': [
                "¡Hola! 👋 Bienvenido a *A Destiempo*. ¿En qué puedo ayudarte hoy?",
                "¡Hola! 👋 Estoy aquí para ayudarte. ¿Buscas algún disco o instrumento?",
            ],
            'despedida': [
                "¡Gracias por contactarnos! 😊 Si tienes más preguntas, no dudes en escribirme.",
                "¡Que tengas un excelente día! 🎵 Si necesitas algo más, aquí estaré.",
            ],
            'ayuda': """📋 *¿En qué puedo ayudarte?*

Puedo ayudarte con:
• 🔍 Buscar productos (discos, instrumentos, refacciones)
• 📦 Verificar disponibilidad y stock
• 💰 Consultar precios
• 📝 Describir productos en detalle
• 🎵 Información sobre artistas y discos

Solo escribe lo que buscas o hazme una pregunta. Por ejemplo:
• "¿Tienes discos de [artista]?"
• "Muéstrame guitarras disponibles"
• "¿Cuánto cuesta [producto]?"
• "¿Tienes stock de [producto]?"

¿Qué te gustaría saber?""",
        }
    
    def procesar_mensaje(self, mensaje):
        """Procesa un mensaje y devuelve una respuesta inteligente"""
        mensaje_lower = mensaje.lower().strip()
        
        # Detectar tipo de consulta
        if self._es_saludo(mensaje_lower):
            return self._responder_saludo()
        
        if self._es_despedida(mensaje_lower):
            return self._responder_despedida()
        
        if self._es_ayuda(mensaje_lower):
            return self.respuestas_generales['ayuda']
        
        # Buscar productos
        productos = self._buscar_productos(mensaje_lower)
        if productos:
            return self._formatear_productos(productos, mensaje_lower)
        
        # Verificar disponibilidad
        if self._es_consulta_disponibilidad(mensaje_lower):
            return self._consultar_disponibilidad(mensaje_lower)
        
        # Consultar precio
        if self._es_consulta_precio(mensaje_lower):
            return self._consultar_precio(mensaje_lower)
        
        # Información sobre artista
        artista_info = self._buscar_artista(mensaje_lower)
        if artista_info:
            return artista_info
        
        # Respuesta por defecto
        return self._respuesta_default(mensaje_lower)
    
    def _es_saludo(self, mensaje):
        """Detecta si es un saludo"""
        saludos = ['hola', 'hi', 'hello', 'buenos días', 'buenas tardes', 'buenas noches', 'buen día']
        return any(saludo in mensaje for saludo in saludos)
    
    def _es_despedida(self, mensaje):
        """Detecta si es una despedida"""
        despedidas = ['adios', 'adiós', 'bye', 'hasta luego', 'chau', 'gracias', 'nos vemos']
        return any(despedida in mensaje for despedida in despedidas)
    
    def _es_ayuda(self, mensaje):
        """Detecta si pide ayuda"""
        ayuda = ['ayuda', 'help', 'menu', 'opciones', 'qué puedes hacer', 'que puedes hacer']
        return any(palabra in mensaje for palabra in ayuda)
    
    def _es_consulta_disponibilidad(self, mensaje):
        """Detecta consultas sobre disponibilidad"""
        palabras = ['disponible', 'stock', 'hay', 'tienes', 'tienen', 'existe', 'existen', 'queda', 'quedan']
        return any(palabra in mensaje for palabra in palabras)
    
    def _es_consulta_precio(self, mensaje):
        """Detecta consultas sobre precio"""
        palabras = ['precio', 'cuesta', 'vale', 'costo', 'cuánto', 'cuanto', 'tarifa']
        return any(palabra in mensaje for palabra in palabras)
    
    def _buscar_productos(self, mensaje):
        """Busca productos en el catálogo"""
        productos = []
        
        # Buscar discos
        discos = self._buscar_discos(mensaje)
        productos.extend([('disco', d) for d in discos[:3]])
        
        # Buscar instrumentos
        instrumentos = self._buscar_instrumentos(mensaje)
        productos.extend([('instrumento', i) for i in instrumentos[:3]])
        
        # Buscar refacciones
        refacciones = self._buscar_refacciones(mensaje)
        productos.extend([('refaccion', r) for r in refacciones[:3]])
        
        return productos[:5]  # Máximo 5 productos
    
    def _buscar_discos(self, mensaje):
        """Busca discos por título, artista o género"""
        query = Q(activo=True)
        
        # Buscar por artista
        artistas = Artista.objects.filter(nombre__icontains=mensaje)
        if artistas.exists():
            query |= Q(artista__in=artistas)
        
        # Buscar por título
        query |= Q(titulo__icontains=mensaje)
        
        # Buscar por género
        query |= Q(genero__nombre__icontains=mensaje)
        
        # Palabras clave
        if any(palabra in mensaje for palabra in ['disco', 'cd', 'vinilo', 'casete', 'album', 'álbum']):
            return Disco.objects.filter(activo=True).order_by('-fecha_agregado')[:5]
        
        return Disco.objects.filter(query).distinct()[:5]
    
    def _buscar_instrumentos(self, mensaje):
        """Busca instrumentos por nombre, marca o categoría"""
        query = Q(activo=True)
        
        # Buscar por nombre
        query |= Q(nombre__icontains=mensaje)
        
        # Buscar por marca
        query |= Q(marca__icontains=mensaje)
        
        # Buscar por categoría
        query |= Q(categoria__nombre__icontains=mensaje)
        
        # Palabras clave comunes
        categorias_keywords = {
            'guitarra': 'Guitarras',
            'bajo': 'Bajos',
            'bateria': 'Baterías',
            'batería': 'Baterías',
            'teclado': 'Teclados',
            'piano': 'Pianos',
            'violin': 'Violines',
            'violín': 'Violines',
            'saxofon': 'Saxofones',
            'saxofón': 'Saxofones',
        }
        
        for keyword, categoria in categorias_keywords.items():
            if keyword in mensaje:
                try:
                    cat = CategoriaInstrumento.objects.get(nombre__icontains=categoria)
                    query |= Q(categoria=cat)
                except:
                    pass
        
        return Instrumento.objects.filter(query).distinct()[:5]
    
    def _buscar_refacciones(self, mensaje):
        """Busca refacciones por nombre, marca o categoría"""
        query = Q(activo=True)
        
        # Buscar por nombre
        query |= Q(nombre__icontains=mensaje)
        
        # Buscar por marca
        query |= Q(marca__icontains=mensaje)
        
        # Buscar por categoría
        query |= Q(categoria__nombre__icontains=mensaje)
        
        # Palabras clave
        if any(palabra in mensaje for palabra in ['refaccion', 'refacción', 'accesorio', 'cuerda', 'cable', 'pedal']):
            return Refaccion.objects.filter(activo=True).order_by('-fecha_agregado')[:5]
        
        return Refaccion.objects.filter(query).distinct()[:5]
    
    def _buscar_artista(self, mensaje):
        """Busca información sobre un artista"""
        artistas = Artista.objects.filter(nombre__icontains=mensaje)[:1]
        if artistas.exists():
            artista = artistas.first()
            discos = Disco.objects.filter(artista=artista, activo=True)[:5]
            
            respuesta = f"🎵 *{artista.nombre}*\n\n"
            
            if artista.biografia:
                respuesta += f"{artista.biografia[:200]}...\n\n"
            
            if discos.exists():
                respuesta += f"*Discos disponibles ({discos.count()}):*\n"
                for disco in discos:
                    stock = "✅ Disponible" if disco.tiene_stock() else "❌ Sin stock"
                    respuesta += f"• {disco.titulo} ({disco.get_formato_display()}) - ${disco.precio} {stock}\n"
            else:
                respuesta += "No tenemos discos de este artista en este momento.\n"
            
            return respuesta
        
        return None
    
    def _formatear_productos(self, productos, mensaje_original):
        """Formatea la lista de productos encontrados"""
        if not productos:
            return "❌ No encontré productos que coincidan con tu búsqueda. ¿Podrías ser más específico?"
        
        respuesta = f"🔍 *Encontré {len(productos)} producto(s):*\n\n"
        
        for tipo, producto in productos:
            if tipo == 'disco':
                respuesta += self._formatear_disco(producto)
            elif tipo == 'instrumento':
                respuesta += self._formatear_instrumento(producto)
            elif tipo == 'refaccion':
                respuesta += self._formatear_refaccion(producto)
            respuesta += "\n"
        
        respuesta += "\n💡 Puedes preguntarme por más detalles de cualquier producto."
        return respuesta
    
    def _formatear_disco(self, disco):
        """Formatea la información de un disco"""
        stock = "✅ Disponible" if disco.tiene_stock() else "❌ Sin stock"
        genero = f" | {disco.genero.nombre}" if disco.genero else ""
        
        respuesta = f"📀 *{disco.artista.nombre} - {disco.titulo}*\n"
        respuesta += f"   Formato: {disco.get_formato_display()}{genero}\n"
        respuesta += f"   Año: {disco.año_lanzamiento}\n"
        respuesta += f"   Precio: ${disco.precio}\n"
        respuesta += f"   {stock}\n"
        
        if disco.descripcion:
            respuesta += f"   {disco.descripcion[:100]}...\n"
        
        return respuesta
    
    def _formatear_instrumento(self, instrumento):
        """Formatea la información de un instrumento"""
        stock = "✅ Disponible" if instrumento.tiene_stock() else "❌ Sin stock"
        
        respuesta = f"🎸 *{instrumento.marca} {instrumento.nombre}*\n"
        if instrumento.modelo:
            respuesta += f"   Modelo: {instrumento.modelo}\n"
        respuesta += f"   Categoría: {instrumento.categoria.nombre}\n"
        respuesta += f"   Estado: {instrumento.get_estado_display()}\n"
        respuesta += f"   Precio: ${instrumento.precio}\n"
        respuesta += f"   {stock}\n"
        
        if instrumento.descripcion:
            respuesta += f"   {instrumento.descripcion[:100]}...\n"
        
        return respuesta
    
    def _formatear_refaccion(self, refaccion):
        """Formatea la información de una refacción"""
        stock = "✅ Disponible" if refaccion.tiene_stock() else "❌ Sin stock"
        
        respuesta = f"🔧 *{refaccion.marca} {refaccion.nombre}*\n"
        respuesta += f"   Categoría: {refaccion.categoria.nombre}\n"
        if refaccion.modelo_compatible:
            respuesta += f"   Compatible con: {refaccion.modelo_compatible}\n"
        respuesta += f"   Precio: ${refaccion.precio}\n"
        respuesta += f"   {stock}\n"
        
        if refaccion.descripcion:
            respuesta += f"   {refaccion.descripcion[:100]}...\n"
        
        return respuesta
    
    def _consultar_disponibilidad(self, mensaje):
        """Consulta disponibilidad de productos"""
        productos = self._buscar_productos(mensaje)
        
        if not productos:
            return "❌ No encontré productos para verificar disponibilidad. ¿Podrías ser más específico?"
        
        respuesta = "📦 *Disponibilidad:*\n\n"
        
        for tipo, producto in productos[:3]:
            if tipo == 'disco':
                nombre = f"{producto.artista.nombre} - {producto.titulo}"
            elif tipo == 'instrumento':
                nombre = f"{producto.marca} {producto.nombre}"
            else:
                nombre = f"{producto.marca} {producto.nombre}"
            
            if producto.tiene_stock():
                stock_total = producto.stock_total
                respuesta += f"✅ *{nombre}*\n   Stock disponible: {stock_total} unidad(es)\n\n"
            else:
                respuesta += f"❌ *{nombre}*\n   Actualmente sin stock\n\n"
        
        return respuesta
    
    def _consultar_precio(self, mensaje):
        """Consulta precios de productos"""
        productos = self._buscar_productos(mensaje)
        
        if not productos:
            return "❌ No encontré productos para consultar precio. ¿Podrías ser más específico?"
        
        respuesta = "💰 *Precios:*\n\n"
        
        for tipo, producto in productos[:3]:
            if tipo == 'disco':
                nombre = f"{producto.artista.nombre} - {producto.titulo}"
            elif tipo == 'instrumento':
                nombre = f"{producto.marca} {producto.nombre}"
            else:
                nombre = f"{producto.marca} {producto.nombre}"
            
            respuesta += f"*{nombre}*\n   Precio: ${producto.precio}\n\n"
        
        return respuesta
    
    def _responder_saludo(self):
        """Responde a un saludo"""
        import random
        return random.choice(self.respuestas_generales['saludo'])
    
    def _responder_despedida(self):
        """Responde a una despedida"""
        import random
        return random.choice(self.respuestas_generales['despedida'])
    
    def _respuesta_default(self, mensaje):
        """Respuesta por defecto cuando no entiende el mensaje"""
        return """🤔 No estoy seguro de entender tu pregunta.

Puedo ayudarte con:
• 🔍 Buscar productos (discos, instrumentos, refacciones)
• 📦 Verificar disponibilidad y stock
• 💰 Consultar precios
• 📝 Describir productos en detalle

Escribe *ayuda* para ver todas las opciones o simplemente escribe lo que buscas.

Por ejemplo:
• "¿Tienes discos de [artista]?"
• "Muéstrame guitarras disponibles"
• "¿Cuánto cuesta [producto]?"

¿En qué puedo ayudarte?"""

