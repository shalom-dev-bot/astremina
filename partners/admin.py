from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Partner, Contract

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'contact_email', 'contact_phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('company_name', 'user__email', 'contact_email')
    readonly_fields = ('created_at',)

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('partner', 'start_date', 'end_date', 'status', 'max_publications', 'is_active')
    list_filter = ('status', 'start_date', 'end_date', 'created_at')
    search_fields = ('partner__company_name', 'partner__user__email')
    readonly_fields = ('created_at',)
    
    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = _('Is Active')