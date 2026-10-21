import base64
import requests
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

@deconstructible
class ImgBBStorage(Storage):
    def _save(self, name, content):
        # Leer el contenido del archivo subido
        content.seek(0)
        file_data = content.read()
        
        # Codificar en base64
        b64_image = base64.b64encode(file_data).decode('utf-8')
        
        # Obtener la API Key
        api_key = getattr(settings, 'IMGBB_API_KEY', None)
        if not api_key:
            raise ValueError("La variable IMGBB_API_KEY no está configurada en settings.py")
        
        # Hacer la petición a ImgBB
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": api_key,
            "image": b64_image,
        }
        
        try:
            response = requests.post(url, data=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                # Retornar la URL de la imagen subida
                return data['data']['url']
            else:
                error_msg = data.get('error', {}).get('message', 'Error desconocido')
                raise ValueError(f"Error de ImgBB: {error_msg}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error de conexión con ImgBB: {str(e)}")

    def _open(self, name, mode='rb'):
        raise NotImplementedError("ImgBBStorage no soporta apertura de archivos locales.")

    def exists(self, name):
        return False

    def url(self, name):
        return name