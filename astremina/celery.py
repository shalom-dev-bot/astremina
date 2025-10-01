import os
from celery import Celery
from django.conf import settings

# Définir le module de configuration par défaut pour Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'astremina.settings')

app = Celery('astremina')

# Charger la configuration depuis settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvrir automatiquement les tâches dans les applications installées
app.autodiscover_tasks()

# Charger la planification Celery Beat dynamiquement
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from scraping.schedule import get_scraping_schedule
    for task_name, task_config in get_scraping_schedule().items():
        sender.add_periodic_task(
            schedule=task_config['schedule'],
            sig=app.signature(task_config['task'], args=task_config.get('args', ())),
            name=task_name,
        )