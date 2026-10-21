import base64
import requests
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

@deconstructible
class ImgBBStorage(Storage):
    def _save(self, name, content):
        content.seek(0)
        file_data = content.read()
        
        # Convertir a base64
        b64_image = base64.b64encode(file_data).decode('utf-8')
        
        api_key = getattr(settings, 'IMGBB_API_KEY', None)
        if not api_key:
            raise ValueError("Falta IMGBB_API_KEY en settings.py")
        
        url = "https://api.imgbb.com/1/upload"
        
        # Enviamos la imagen como un formulario multipart (más compatible)
        files = {
            'image': (name, file_data, 'image/jpeg')
        }
        data = {
            'key': api_key
        }
        
        # Añadimos un User-Agent de navegador para evitar bloqueos por bot
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        try:
            response = requests.post(url, data=data, files=files, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                return result['data']['url']
            else:
                error_msg = result.get('error', {}).get('message', 'Error desconocido')
                raise ValueError(f"Error de ImgBB: {error_msg}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error de conexión con ImgBB: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error inesperado al subir a ImgBB: {str(e)}")

    def _open(self, name, mode='rb'):
        raise NotImplementedError("ImgBBStorage no soporta apertura de archivos locales.")

    def exists(self, name):
        return False

    def url(self, name):
        return name