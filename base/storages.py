import requests
import uuid
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

@deconstructible
class SupabaseStorage(Storage):
    def __init__(self, *args, **kwargs):
        self.base_url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_KEY
        self.bucket = "media"

    def _save(self, name, content):
        content.seek(0)
        file_data = content.read()
        
        # Generar un nombre único usando UUID
        ext = name.split('.')[-1] if '.' in name else 'jpg'
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        
        upload_url = f"{self.base_url}/storage/v1/object/{self.bucket}/{unique_name}"
        
        headers = {
            "apikey": self.key,
            "Content-Type": "application/octet-stream",
        }
        
        response = requests.post(upload_url, headers=headers, data=file_data, timeout=30)
        if response.status_code not in (200, 201):
            raise ValueError(f"Error Supabase: {response.status_code} - {response.text}")
        
        return f"{self.base_url}/storage/v1/object/public/{self.bucket}/{unique_name}"

    def _open(self, name, mode='rb'):
        raise NotImplementedError("SupabaseStorage no soporta apertura local.")

    def exists(self, name):
        return False

    def url(self, name):
        if not name:
            return ""
        if name.startswith("http"):
            return name
        return f"{self.base_url}/storage/v1/object/public/{self.bucket}/{name}"