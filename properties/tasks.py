from celery import shared_task
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
from .models import PropertyImage
import os

@shared_task
def process_images(image_id):
    """Redimensionne l'image et génère une vignette"""
    try:
        image_obj = PropertyImage.objects.get(id=image_id)
        img = Image.open(image_obj.image)
        
        # Redimensionner l'image principale (max 1200x1200)
        img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
        buffer = BytesIO()
        img.save(buffer, format=img.format or 'JPEG', quality=85)
        image_name = os.path.basename(image_obj.image.name)
        image_obj.image.save(image_name, ContentFile(buffer.getvalue()), save=True)
        
        # Générer une vignette (200x200)
        thumb = img.copy()
        thumb.thumbnail((200, 200), Image.Resampling.LANCZOS)
        thumb_buffer = BytesIO()
        thumb.save(thumb_buffer, format=img.format or 'JPEG', quality=85)
        thumb_name = f"thumb_{image_name}"
        image_obj.thumbnail.save(thumb_name, ContentFile(thumb_buffer.getvalue()), save=True)
        
    except Exception as e:
        print(f"Error processing image {image_id}: {str(e)}")