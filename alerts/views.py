from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from .models import PropertyAlert
from .forms import PropertyAlertForm

@login_required
def create_alert(request):
    """Créer une nouvelle alerte de recherche"""
    if request.method == 'POST':
        form = PropertyAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.user = request.user
            alert.save()
            messages.success(request, _('Alert created successfully.'))
            return redirect('accounts:profile')
    else:
        form = PropertyAlertForm()
    
    context = {
        'form': form,
        'title': _('Create Property Alert'),
    }
    return render(request, 'alerts/create_alert.html', context)

@login_required
def edit_alert(request, alert_id):
    """Modifier une alerte existante"""
    alert = get_object_or_404(PropertyAlert, id=alert_id, user=request.user)
    if request.method == 'POST':
        form = PropertyAlertForm(request.POST, instance=alert)
        if form.is_valid():
            form.save()
            messages.success(request, _('Alert updated successfully.'))
            return redirect('accounts:profile')
    else:
        form = PropertyAlertForm(instance=alert)
    
    context = {
        'form': form,
        'title': _('Edit Property Alert'),
    }
    return render(request, 'alerts/edit_alert.html', context)

@login_required
def delete_alert(request, alert_id):
    """Supprimer une alerte"""
    alert = get_object_or_404(PropertyAlert, id=alert_id, user=request.user)
    if request.method == 'POST':
        alert.delete()
        messages.success(request, _('Alert deleted successfully.'))
        return redirect('accounts:profile')
    
    context = {
        'alert': alert,
        'title': _('Delete Property Alert'),
    }
    return render(request, 'alerts/delete_alert.html', context)