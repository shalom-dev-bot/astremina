from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

class Partner(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='partner_profile',
        verbose_name=_('user')
    )
    company_name = models.CharField(_('company name'), max_length=200)
    address = models.TextField(_('address'))
    contact_email = models.EmailField(_('contact email'))
    contact_phone = models.CharField(_('contact phone'), max_length=20)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Partner')
        verbose_name_plural = _('Partners')

    def __str__(self):
        return self.company_name

class Contract(models.Model):
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('suspended', _('Suspended')),
        ('expired', _('Expired')),
    ]
    
    partner = models.ForeignKey(
        Partner, 
        on_delete=models.CASCADE, 
        related_name='contracts',
        verbose_name=_('partner')
    )
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    status = models.CharField(
        _('status'), 
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='active'
    )
    max_publications = models.PositiveIntegerField(
        _('max publications'), 
        blank=True, 
        null=True,
        help_text=_('Maximum number of properties this partner can publish')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Contract')
        verbose_name_plural = _('Contracts')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.partner.company_name} - {self.start_date} to {self.end_date}"

    @property
    def is_active(self):
        from django.utils import timezone
        today = timezone.now().date()
        return (
            self.status == 'active' and 
            self.start_date <= today <= self.end_date
        )