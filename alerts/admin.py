from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import PropertyAlert

@admin.register(PropertyAlert)
class PropertyAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'property_type', 'min_price', 'max_price', 'min_bedrooms', 'is_active', 'created_at')
    list_filter = ('is_active', 'city', 'property_type')
    search_fields = ('user__email', 'city')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ['-created_at']

    class Meta:
        verbose_name = _('Property Alert')
        verbose_name_plural = _('Property Alerts')