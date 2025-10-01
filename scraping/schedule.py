from celery.schedules import crontab
from .tasks import scrape_source
from .models import ScrapingSource

def get_scraping_schedule():
    """Génère dynamiquement le planning des tâches de scraping"""
    schedule = {}
    sources = ScrapingSource.objects.filter(active=True)
    
    for source in sources:
        schedule[f"scrape-{source.id}"] = {
            'task': 'scraping.tasks.scrape_source',
            'schedule': crontab(hour=0, minute=0),  # Tous les jours à minuit
            'args': (source.id,),
        }
    
    return schedule