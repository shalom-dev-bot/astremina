from django.db import models
from django.utils.translation import gettext_lazy as _

class ScrapingSource(models.Model):
    TYPE_CHOICES = [
        ('real_estate', _('Real Estate')),
        ('hotel', _('Hotel')),
    ]
    
    name = models.CharField(_('name'), max_length=100)
    base_url = models.URLField(_('base URL'))
    type = models.CharField(_('type'), max_length=20, choices=TYPE_CHOICES)
    last_scraped = models.DateTimeField(_('last scraped'), blank=True, null=True)
    scraper_config = models.JSONField(
        _('scraper configuration'), 
        blank=True, 
        null=True,
        help_text=_('CSS selectors and scraping rules')
    )
    active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Scraping Source')
        verbose_name_plural = _('Scraping Sources')

    def __str__(self):
        return self.name

class ScrapeJobLog(models.Model):
    STATUS_CHOICES = [
        ('running', _('Running')),
        ('success', _('Success')),
        ('failed', _('Failed')),
    ]
    
    source = models.ForeignKey(
        ScrapingSource, 
        on_delete=models.CASCADE, 
        related_name='job_logs',
        verbose_name=_('source')
    )
    started_at = models.DateTimeField(_('started at'), auto_now_add=True)
    finished_at = models.DateTimeField(_('finished at'), blank=True, null=True)
    status = models.CharField(_('status'), max_length=10, choices=STATUS_CHOICES, default='running')
    items_extracted = models.PositiveIntegerField(_('items extracted'), default=0)
    items_created = models.PositiveIntegerField(_('items created'), default=0)
    items_updated = models.PositiveIntegerField(_('items updated'), default=0)
    errors = models.TextField(_('errors'), blank=True)

    class Meta:
        verbose_name = _('Scrape Job Log')
        verbose_name_plural = _('Scrape Job Logs')
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.source.name} - {self.started_at}"