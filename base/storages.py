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
        
        # Codificar en base64 (método estándar para ImgBB)
        b64_image = base64.b64encode(file_data).decode('utf-8')
        
        api_key = getattr(settings, 'IMGBB_API_KEY', None)
        if not api_key:
            raise ValueError("Falta IMGBB_API_KEY en settings.py")
        
        url = "https://api.imgbb.com/1/upload"
        
        # Enviar como formulario estándar (data=payload), SIN User-Agent de navegador
        payload = {
            'key': api_key,
            'image': b64_image,
        }
        
        try:
            response = requests.post(url, data=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                return result['data']['url']
            else:
                error_msg = result.get('error', {}).get('message', 'Error desconocido')
                raise ValueError(f"Error de ImgBB: {error_msg}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error de conexión con ImgBB: {str(e)}")

    def _open(self, name, mode='rb'):
        raise NotImplementedError("ImgBBStorage no soporta apertura local.")

    def exists(self, name):
        return False

    def url(self, name):
        return name