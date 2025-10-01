from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from properties.models import Property
from .models import Partner, Contract

@login_required
def dashboard(request):
    """Dashboard partenaire"""
    if not request.user.is_partner:
        messages.error(request, _('You need to be a partner to access this page.'))
        return redirect('properties:home')
    
    try:
        partner = request.user.partner_profile
    except Partner.DoesNotExist:
        messages.error(request, _('Partner profile not found.'))
        return redirect('properties:home')
    
    # Statistiques
    total_properties = Property.objects.filter(owner=request.user).count()
    published_properties = Property.objects.filter(owner=request.user, status='published').count()
    draft_properties = Property.objects.filter(owner=request.user, status='draft').count()
    
    # Contrats
    contracts = Contract.objects.filter(partner=partner).order_by('-created_at')
    active_contract = contracts.filter(status='active').first()
    
    # Propriétés récentes
    recent_properties = Property.objects.filter(owner=request.user).order_by('-created_at')[:5]
    
    context = {
        'partner': partner,
        'total_properties': total_properties,
        'published_properties': published_properties,
        'draft_properties': draft_properties,
        'contracts': contracts,
        'active_contract': active_contract,
        'recent_properties': recent_properties,
    }
    
    return render(request, 'partners/dashboard.html', context)

@login_required
def my_properties(request):
    """Liste des propriétés du partenaire"""
    if not request.user.is_partner:
        messages.error(request, _('You need to be a partner to access this page.'))
        return redirect('properties:home')
    
    properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(properties, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'partners/my_properties.html', context)