from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Property
from scraping.tasks import geocode_property

@receiver(post_save, sender=Property)
def property_post_save(sender, instance, created, **kwargs):
    """Déclenche des actions après la sauvegarde d'une propriété"""
    if created and instance.address and instance.city:
        # Lancer la tâche de géocodage si l'adresse est présente
        geocode_property.delay(instance.id)