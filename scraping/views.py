from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from .models import ScrapingSource, ScrapeJobLog
from .tasks import scrape_source

@login_required
@user_passes_test(lambda u: u.is_superuser)
def scraping_source_list(request):
    """Liste des sources de scraping"""
    sources = ScrapingSource.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(sources, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': _('Scraping Sources'),
    }
    
    return render(request, 'scraping/source_list.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def scraping_source_detail(request, source_id):
    """Détail d'une source et ses logs"""
    source = get_object_or_404(ScrapingSource, id=source_id)
    logs = source.job_logs.order_by('-started_at')
    
    # Pagination pour les logs
    paginator = Paginator(logs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'source': source,
        'page_obj': page_obj,
        'title': _('Scraping Source: {}').format(source.name),
    }
    
    return render(request, 'scraping/source_detail.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def trigger_scraping(request, source_id):
    """Déclenche manuellement une tâche de scraping"""
    source = get_object_or_404(ScrapingSource, id=source_id)
    if not source.active:
        messages.error(request, _('This source is not active.'))
        return redirect('scraping:source_list')
    
    # Lancer la tâche Celery
    scrape_source.delay(source_id)
    messages.success(request, _('Scraping task triggered for {}.').format(source.name))
    return redirect('scraping:source_detail', source_id=source_id)