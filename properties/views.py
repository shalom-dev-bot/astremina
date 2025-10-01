from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from .models import Property, Favorite
from .forms import PropertySearchForm, PropertyForm, PropertyImageForm
from .tasks import process_images

def home(request):
    """Page d'accueil avec recherche et propriétés récentes"""
    search_form = PropertySearchForm(request.GET or None)
    properties = Property.objects.filter(status='published').select_related('owner').prefetch_related('images')
    
    if search_form.is_valid():
        city = search_form.cleaned_data.get('city')
        property_type = search_form.cleaned_data.get('property_type')
        min_price = search_form.cleaned_data.get('min_price')
        max_price = search_form.cleaned_data.get('max_price')
        
        if city:
            properties = properties.filter(city__icontains=city)
        if property_type:
            properties = properties.filter(property_type=property_type)
        if min_price:
            properties = properties.filter(price__gte=min_price)
        if max_price:
            properties = properties.filter(price__lte=max_price)
    
    # Pagination
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Propriétés récentes pour la page d'accueil
    recent_properties = Property.objects.filter(status='published')[:6]
    
    context = {
        'search_form': search_form,
        'page_obj': page_obj,
        'recent_properties': recent_properties,
        'is_search': bool(request.GET),
    }
    
    return render(request, 'properties/home.html', context)

def property_detail(request, slug):
    """Page de détail d'une propriété"""
    property_obj = get_object_or_404(
        Property.objects.select_related('owner').prefetch_related('images'),
        slug=slug,
        status='published'
    )
    
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(
            user=request.user, 
            property=property_obj
        ).exists()
    
    # Propriétés similaires
    similar_properties = Property.objects.filter(
        city=property_obj.city,
        property_type=property_obj.property_type,
        status='published'
    ).exclude(id=property_obj.id)[:4]
    
    context = {
        'property': property_obj,
        'is_favorite': is_favorite,
        'similar_properties': similar_properties,
    }
    
    return render(request, 'properties/detail.html', context)

def property_list(request):
    """Liste des propriétés avec filtres"""
    search_form = PropertySearchForm(request.GET or None)
    properties = Property.objects.filter(status='published').select_related('owner').prefetch_related('images')
    
    if search_form.is_valid():
        city = search_form.cleaned_data.get('city')
        property_type = search_form.cleaned_data.get('property_type')
        min_price = search_form.cleaned_data.get('min_price')
        max_price = search_form.cleaned_data.get('max_price')
        bedrooms = search_form.cleaned_data.get('bedrooms')
        
        if city:
            properties = properties.filter(city__icontains=city)
        if property_type:
            properties = properties.filter(property_type=property_type)
        if min_price:
            properties = properties.filter(price__gte=min_price)
        if max_price:
            properties = properties.filter(price__lte=max_price)
        if bedrooms:
            properties = properties.filter(bedrooms__gte=bedrooms)
    
    # Pagination
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'search_form': search_form,
        'page_obj': page_obj,
    }
    
    return render(request, 'properties/list.html', context)

def map_view(request):
    """Vue carte des propriétés"""
    properties = Property.objects.filter(
        status='published',
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related('owner').prefetch_related('images')
    
    context = {
        'properties': properties,
    }
    
    return render(request, 'properties/map.html', context)

@login_required
def favorites(request):
    """Liste des favoris de l'utilisateur"""
    favorites = Favorite.objects.filter(user=request.user).select_related('property').prefetch_related('property__images')
    
    paginator = Paginator(favorites, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'properties/favorites.html', context)

@login_required
def property_create(request):
    """Créer une nouvelle propriété"""
    if not hasattr(request.user, 'partner') or not request.user.partner.is_active:
        messages.error(request, _('You must be an active partner to create properties.'))
        return redirect('home')
    
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        image_form = PropertyImageForm(request.POST, request.FILES)
        if form.is_valid() and image_form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            property_obj.status = 'published'
            property_obj.save()
            
            if image_form.cleaned_data.get('image'):
                image_obj = image_form.save(commit=False)
                image_obj.property = property_obj
                image_obj.save()
                # Déclencher la tâche Celery pour redimensionner l'image
                process_images.delay(image_obj.id)
                
            messages.success(request, _('Property created successfully.'))
            return redirect('partners:my_properties')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = PropertyForm()
        image_form = PropertyImageForm()
    
    return render(request, 'properties/create.html', {
        'form': form,
        'image_form': image_form,
    })

@login_required
def property_edit(request, slug):
    """Modifier une propriété existante"""
    property_obj = get_object_or_404(Property, slug=slug, owner=request.user)
    if not hasattr(request.user, 'partner') or not request.user.partner.is_active:
        messages.error(request, _('You must be an active partner to edit properties.'))
        return redirect('home')
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property_obj)
        image_form = PropertyImageForm(request.POST, request.FILES)
        if form.is_valid() and image_form.is_valid():
            form.save()
            if image_form.cleaned_data.get('image'):
                image_obj = image_form.save(commit=False)
                image_obj.property = property_obj
                image_obj.save()
                # Déclencher la tâche Celery pour redimensionner l'image
                process_images.delay(image_obj.id)
            messages.success(request, _('Property updated successfully.'))
            return redirect('partners:my_properties')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = PropertyForm(instance=property_obj)
        image_form = PropertyImageForm()
    
    return render(request, 'properties/edit.html', {
        'form': form,
        'image_form': image_form,
        'property': property_obj,
    })

@login_required
def property_delete(request, slug):
    """Supprimer une propriété"""
    property_obj = get_object_or_404(Property, slug=slug, owner=request.user)
    if not hasattr(request.user, 'partner') or not request.user.partner.is_active:
        messages.error(request, _('You must be an active partner to delete properties.'))
        return redirect('home')
    
    if request.method == 'POST':
        property_obj.delete()
        messages.success(request, _('Property deleted successfully.'))
        return redirect('partners:my_properties')
    
    return render(request, 'properties/delete.html', {'property': property_obj})