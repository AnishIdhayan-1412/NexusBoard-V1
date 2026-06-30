"""
Custom Cloudinary storage backend compatible with Django 5+/6.
Replaces django-cloudinary-storage which broke on Django 6.
"""
import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.core.files.storage import Storage
from django.conf import settings
import os


class CloudinaryMediaStorage(Storage):
    """
    Django 6-compatible Cloudinary storage for media files.
    Stores files in Cloudinary, returns persistent CDN URLs.
    """

    def _get_public_id(self, name):
        # Strip extension — Cloudinary stores by public_id without extension
        root, _ = os.path.splitext(name)
        return root.replace('\\', '/')

    def _open(self, name, mode='rb'):
        raise NotImplementedError("Direct file reading not supported via Cloudinary.")

    def _save(self, name, content):
        public_id = self._get_public_id(name)
        # Read content into bytes
        content.seek(0)
        result = cloudinary.uploader.upload(
            content,
            public_id=public_id,
            overwrite=True,
            resource_type='image',
        )
        # Store the full public_id with extension info stripped
        # Return name so Django saves it in the DB field
        return name

    def delete(self, name):
        public_id = self._get_public_id(name)
        try:
            cloudinary.api.delete_resources([public_id])
        except Exception:
            pass

    def exists(self, name):
        try:
            public_id = self._get_public_id(name)
            cloudinary.api.resource(public_id)
            return True
        except cloudinary.api.NotFound:
            return False
        except Exception:
            return False

    def url(self, name):
        public_id = self._get_public_id(name)
        return cloudinary.CloudinaryImage(public_id).build_url(secure=True)

    def size(self, name):
        try:
            public_id = self._get_public_id(name)
            resource = cloudinary.api.resource(public_id)
            return resource.get('bytes', 0)
        except Exception:
            return 0
