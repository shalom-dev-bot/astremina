from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ScrapingSource, ScrapeJobLog

@admin.register(ScrapingSource)
class ScrapingSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'base_url', 'active', 'last_scraped', 'created_at')
    list_filter = ('type', 'active', 'created_at')
    search_fields = ('name', 'base_url')
    readonly_fields = ('last_scraped', 'created_at')

@admin.register(ScrapeJobLog)
class ScrapeJobLogAdmin(admin.ModelAdmin):
    list_display = ('source', 'status', 'items_extracted', 'items_created', 'items_updated', 'started_at', 'finished_at')
    list_filter = ('status', 'started_at')
    search_fields = ('source__name',)
    readonly_fields = ('started_at', 'finished_at')