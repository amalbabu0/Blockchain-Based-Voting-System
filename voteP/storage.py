import os
import uuid

import requests
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

BLOB_API_URL = "https://vercel.com/api/blob"
BLOB_API_VERSION = "13"


def _store_id_from_token(token):
    parts = token.split("_")
    return parts[3] if len(parts) > 3 else ""


@deconstructible
class VercelBlobStorage(Storage):
    """Stores files in Vercel Blob instead of local disk.

    Vercel's filesystem is read-only/ephemeral, so FileSystemStorage can't
    persist uploads there. Only the relative pathname (not the full blob
    URL) is kept as the field's name, since the img columns are varchar(100)
    and a full blob URL would overflow that.
    """

    def _token(self):
        token = os.environ.get("BLOB_READ_WRITE_TOKEN")
        if not token:
            raise RuntimeError("BLOB_READ_WRITE_TOKEN is not set")
        return token

    def _headers(self, extra=None):
        token = self._token()
        headers = {
            "authorization": f"Bearer {token}",
            "x-api-version": BLOB_API_VERSION,
            "x-vercel-blob-store-id": _store_id_from_token(token),
            "x-api-blob-request-id": uuid.uuid4().hex,
        }
        if extra:
            headers.update(extra)
        return headers

    def get_available_name(self, name, max_length=None):
        directory, filename = os.path.split(name)
        base, ext = os.path.splitext(filename)
        unique_name = f"{base}-{uuid.uuid4().hex[:8]}{ext}"
        return os.path.join(directory, unique_name) if directory else unique_name

    def _save(self, name, content):
        content.seek(0)
        data = content.read()
        content_type = getattr(content, "content_type", None) or "application/octet-stream"
        resp = requests.put(
            f"{BLOB_API_URL}/",
            params={"pathname": name},
            headers=self._headers({
                "x-vercel-blob-access": "public",
                "x-add-random-suffix": "0",
                "x-allow-overwrite": "1",
                "x-content-type": content_type,
            }),
            data=data,
            timeout=30,
        )
        resp.raise_for_status()
        return name

    def _open(self, name, mode="rb"):
        resp = requests.get(self.url(name), timeout=30)
        resp.raise_for_status()
        return ContentFile(resp.content)

    def exists(self, name):
        return False

    def url(self, name):
        store_id = _store_id_from_token(self._token())
        return f"https://{store_id}.public.blob.vercel-storage.com/{name}"

    def delete(self, name):
        try:
            requests.post(
                f"{BLOB_API_URL}/delete",
                headers=self._headers({"content-type": "application/json"}),
                json={"urls": [self.url(name)]},
                timeout=30,
            )
        except requests.RequestException:
            pass

    def size(self, name):
        return 0

    def get_accessed_time(self, name):
        raise NotImplementedError

    def get_created_time(self, name):
        raise NotImplementedError

    def get_modified_time(self, name):
        raise NotImplementedError
