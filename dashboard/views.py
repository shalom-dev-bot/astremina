from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from properties.models import Property
from partners.models import Partner, Contract
from scraping.models import ScrapeJobLog
from .models import DailyStats

User = get_user_model()

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    """Dashboard administrateur"""
    # Statistiques utilisateurs (temps réel)
    total_users = User.objects.count()
    thirty_days_ago = timezone.now() - timedelta(days=30)
    active_users_30d = User.objects.filter(last_login__gte=thirty_days_ago).count()
    new_users_30d = User.objects.filter(date_joined__gte=thirty_days_ago).count()

    # Statistiques propriétés (temps réel)
    total_properties = Property.objects.count()
    published_properties = Property.objects.filter(status='published').count()
    avg_property_price = Property.objects.filter(status='published').aggregate(Avg('price'))['price__avg'] or 0
    properties_by_city = Property.objects.values('city').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    # Statistiques partenaires (temps réel)
    total_partners = Partner.objects.count()
    active_contracts = Contract.objects.filter(status='active').count()
    expired_contracts = Contract.objects.filter(status='expired').count()

    # Dernières stats agrégées (depuis DailyStats)
    latest_stats = DailyStats.objects.order_by('-date').first()

    # Logs de scraping récents (avec pagination)
    recent_scrape_logs = ScrapeJobLog.objects.select_related('source').order_by('-started_at')
    scrape_paginator = Paginator(recent_scrape_logs, 10)
    scrape_page_number = request.GET.get('scrape_page')
    scrape_page_obj = scrape_paginator.get_page(scrape_page_number)

    # Propriétés récentes (avec pagination)
    recent_properties = Property.objects.select_related('owner').order_by('-created_at')
    property_paginator = Paginator(recent_properties, 10)
    property_page_number = request.GET.get('property_page')
    property_page_obj = property_paginator.get_page(property_page_number)

    context = {
        'title': _('Admin Dashboard'),
        'total_users': total_users,
        'active_users_30d': active_users_30d,
        'new_users_30d': new_users_30d,
        'total_properties': total_properties,
        'published_properties': published_properties,
        'avg_property_price': round(avg_property_price, 2),
        'properties_by_city': properties_by_city,
        'total_partners': total_partners,
        'active_contracts': active_contracts,
        'expired_contracts': expired_contracts,
        'latest_stats': latest_stats,
        'scrape_page_obj': scrape_page_obj,
        'property_page_obj': property_page_obj,
    }

    return render(request, 'dashboard/admin_dashboard.html', context)