from django.conf import settings
from .models import ServerSelection
from django.db import connections
import socket

def url_principal(request):
    """Devuelve la URL principal del sitio."""
    current_domain = f"{request.scheme}://{request.get_host()}"
    return {'URL_PRINCIPAL': current_domain}

def configuracion_global(request):
    """Devuelve configuraciones globales como el nombre del servidor y el año actual."""
    return {
        'NOMBRE_SERVIDOR': settings.NOMBRE_SERVIDOR,
        'ANIO_ACTUAL': settings.ANIO_ACTUAL,
    }

def get_server_info(request):
    """Devuelve información del servidor para que esté disponible en todas las plantillas."""
    server_selection = ServerSelection.objects.first()
    
    online_count = 0
    if server_selection:
        # Obtener la cantidad de personajes en línea
        try:
            with connections['acore_characters'].cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM characters WHERE online = 1")
                result = cursor.fetchone()
                if result is not None:
                    online_count = result[0]
        except Exception as e:
            # Manejar errores de conexión o consulta
            print(f"Error al obtener personajes en línea: {e}")
    
    return {
        'server': server_selection,
        'online_characters': online_count,
        'expansion': 'WotLK' if server_selection and server_selection.gamebuild == 12340 else 'Cataclysm',
    }
