from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from properties.models import Property

User = get_user_model()

class PropertyAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_alerts', verbose_name=_('user'))
    city = models.CharField(_('city'), max_length=100, blank=True)
    property_type = models.CharField(_('property type'), max_length=50, blank=True)
    min_price = models.DecimalField(_('minimum price'), max_digits=12, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField(_('maximum price'), max_digits=12, decimal_places=2, null=True, blank=True)
    min_bedrooms = models.PositiveIntegerField(_('minimum bedrooms'), null=True, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Property Alert')
        verbose_name_plural = _('Property Alerts')
        ordering = ['-created_at']

    def __str__(self):
        return f"Alert for {self.user.email} in {self.city or 'Any city'}"