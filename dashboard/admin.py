from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import DailyStats

@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_users', 'active_users_30d', 'new_users_30d', 'total_properties', 'published_properties', 'new_properties_24h', 'total_partners', 'active_contracts', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('date',)
    readonly_fields = ('date', 'total_users', 'active_users_30d', 'new_users_30d', 'total_properties', 'published_properties', 'new_properties_24h', 'total_partners', 'active_contracts', 'created_at')
    ordering = ['-date']

    class Meta:
        verbose_name = _('Daily Stats')
        verbose_name_plural = _('Daily Stats')