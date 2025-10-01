from django.db import models
from django.utils.translation import gettext_lazy as _

class DailyStats(models.Model):
    date = models.DateField(_('date'), unique=True)
    total_users = models.PositiveIntegerField(_('total users'), default=0)
    active_users_30d = models.PositiveIntegerField(_('active users (30 days)'), default=0)
    new_users_30d = models.PositiveIntegerField(_('new users (30 days)'), default=0)
    total_properties = models.PositiveIntegerField(_('total properties'), default=0)
    published_properties = models.PositiveIntegerField(_('published properties'), default=0)
    new_properties_24h = models.PositiveIntegerField(_('new properties (24h)'), default=0)
    total_partners = models.PositiveIntegerField(_('total partners'), default=0)
    active_contracts = models.PositiveIntegerField(_('active contracts'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Daily Stats')
        verbose_name_plural = _('Daily Stats')
        ordering = ['-date']

    def __str__(self):
        return f"Stats for {self.date}"