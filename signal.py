from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from .models import Place, Image
import requests


@receiver(pre_save, sender=Image)
def update_image_metadata(sender, instance, **kwargs):
    """Fetch and update image dimensions from IIIF info.json if not set."""
    
    if (instance.width is None or instance.height is None) and instance.iiif_file:
        base_url = "https://img.dh.gu.se/diana/static/"
        iiif_file_url = getattr(instance.iiif_file, 'url', None)
        if not iiif_file_url:
            return
        if not iiif_file_url.startswith("http"):
            iiif_file_url = base_url + iiif_file_url.lstrip("/")
        info_url = f"{iiif_file_url}/info.json"
        try:
            response = requests.get(info_url, timeout=5)
            if response.status_code == 200:
                info = response.json()
                width = info.get("width")
                height = info.get("height")
                # Only update if values are present
                if width and height:
                    # Schedule this to run after the current transaction commits
                    # This ensures M2M fields are saved first
                    def update_dimensions():
                        Image.objects.filter(pk=instance.pk).update(width=width, height=height)
                    
                    transaction.on_commit(update_dimensions)
        except Exception as e:
            # Optionally log the error
            print(f"Could not fetch IIIF info for image {instance.id}: {e}")