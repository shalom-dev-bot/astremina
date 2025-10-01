from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import PropertyAlert
from properties.models import Property
import logging

logger = logging.getLogger(__name__)

@shared_task
def alerts_match_and_notify():
    """Vérifie les nouvelles propriétés et notifie les utilisateurs avec des alertes correspondantes"""
    try:
        # Récupérer les alertes actives
        alerts = PropertyAlert.objects.filter(is_active=True)
        one_day_ago = timezone.now() - timezone.timedelta(days=1)

        for alert in alerts:
            # Construire la requête de correspondance
            query = Property.objects.filter(
                status='published',
                created_at__gte=one_day_ago
            )
            if alert.city:
                query = query.filter(city__icontains=alert.city)
            if alert.property_type:
                query = query.filter(property_type=alert.property_type)
            if alert.min_price:
                query = query.filter(price__gte=alert.min_price)
            if alert.max_price:
                query = query.filter(price__lte=alert.max_price)
            if alert.min_bedrooms:
                query = query.filter(bedrooms__gte=alert.min_bedrooms)

            # Si des propriétés correspondent
            properties = query[:10]  # Limiter à 10 pour éviter trop d'emails
            if properties:
                # Construire le message
                subject = f"New Properties Matching Your Alert"
                message = f"Dear {alert.user.email},\n\nWe found new properties matching your criteria:\n\n"
                for prop in properties:
                    message += f"- {prop.title} ({prop.city}, {prop.price} XAF)\n"
                message += f"\nView more details at {settings.SITE_URL}\n\nBest regards,\nAstremina Team"

                # Envoyer l'email
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [alert.user.email],
                    fail_silently=False,
                )
                logger.info(f"Sent notification to {alert.user.email} for {len(properties)} matching properties")

    except Exception as e:
        logger.error(f"Error in alerts_match_and_notify: {str(e)}")