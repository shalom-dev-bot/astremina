from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from rest_framework import viewsets, permissions
from .models import PropertyAlert
from .forms import PropertyAlertForm
from api.serializers import PropertyAlertSerializer

@login_required
def list_alerts(request):
    """Lister les alertes de l'utilisateur"""
    alerts = PropertyAlert.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'alerts': alerts,
        'title': _('My Property Alerts'),
    }
    return render(request, 'alerts/list_alerts.html', context)

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
            return redirect('alerts:list_alerts')
        else:
            messages.error(request, _('Please correct the errors below.'))
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
            return redirect('alerts:list_alerts')
        else:
            messages.error(request, _('Please correct the errors below.'))
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
        return redirect('alerts:list_alerts')
    
    context = {
        'alert': alert,
        'title': _('Delete Property Alert'),
    }
    return render(request, 'alerts/delete_alert.html', context)

class AlertViewSet(viewsets.ModelViewSet):
    """API pour gérer les alertes"""
    serializer_class = PropertyAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PropertyAlert.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)