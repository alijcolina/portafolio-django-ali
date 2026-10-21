import requests
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

@deconstructible
class SupabaseStorage(Storage):
    def __init__(self, *args, **kwargs):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_KEY
        self.bucket = "media"

    def _save(self, name, content):
        content.seek(0)
        file_data = content.read()
        file_name = name.replace(" ", "_")
        
        upload_url = f"{self.url}/storage/v1/object/{self.bucket}/{file_name}"
        
        # CORREGIDO: Usar el encabezado 'apikey' en lugar de 'Authorization: Bearer'
        headers = {
            "apikey": self.key,
            "Content-Type": "application/octet-stream",
        }
        
        response = requests.post(upload_url, headers=headers, data=file_data, timeout=30)
        if response.status_code not in (200, 201):
            raise ValueError(f"Error Supabase: {response.status_code} - {response.text}")
        
        return f"{self.url}/storage/v1/object/public/{self.bucket}/{file_name}"

    def _open(self, name, mode='rb'):
        raise NotImplementedError("SupabaseStorage no soporta apertura local.")

    def exists(self, name):
        return False

    def url(self, name):
        return name