from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import uuid

User = get_user_model()

class Property(models.Model):
    PROPERTY_TYPES = [
        ('house', _('House')),
        ('apartment', _('Apartment')),
        ('land', _('Land')),
        ('hotel', _('Hotel')),
        ('office', _('Office')),
        ('commercial', _('Commercial')),
    ]
    
    STATUS_CHOICES = [
        ('published', _('Published')),
        ('draft', _('Draft')),
        ('disabled', _('Disabled')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=220, unique=True, blank=True)
    description = models.TextField(_('description'))
    property_type = models.CharField(
        _('property type'), 
        max_length=20, 
        choices=PROPERTY_TYPES
    )
    price = models.DecimalField(_('price'), max_digits=12, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=3, default='XAF')
    city = models.CharField(_('city'), max_length=100)
    neighborhood = models.CharField(_('neighborhood'), max_length=100, blank=True)
    address = models.TextField(_('address'), blank=True)
    latitude = models.DecimalField(
        _('latitude'), 
        max_digits=10, 
        decimal_places=8, 
        blank=True, 
        null=True
    )
    longitude = models.DecimalField(
        _('longitude'), 
        max_digits=11, 
        decimal_places=8, 
        blank=True, 
        null=True
    )
    bedrooms = models.PositiveIntegerField(_('bedrooms'), blank=True, null=True)
    bathrooms = models.PositiveIntegerField(_('bathrooms'), blank=True, null=True)
    surface_area = models.PositiveIntegerField(_('surface area (m²)'), blank=True, null=True)
    status = models.CharField(
        _('status'), 
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='published'
    )
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='properties',
        verbose_name=_('owner')
    )
    source = models.ForeignKey(
        'scraping.ScrapingSource', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        verbose_name=_('source')
    )
    source_url = models.URLField(_('source URL'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Property')
        verbose_name_plural = _('Properties')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['property_type']),
            models.Index(fields=['price']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name=_('property')
    )
    image = models.ImageField(_('image'), upload_to='properties/')
    thumbnail = models.ImageField(_('thumbnail'), upload_to='properties/thumbnails/', blank=True, null=True)
    is_primary = models.BooleanField(_('is primary'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Property Image')
        verbose_name_plural = _('Property Images')
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"Image for {self.property.title}"

class Favorite(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='favorites',
        verbose_name=_('user')
    )
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name='favorited_by',
        verbose_name=_('property')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Favorite')
        verbose_name_plural = _('Favorites')
        unique_together = ['user', 'property']

    def __str__(self):
        return f"{self.user.email} - {self.property.title}"

class Alert(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='alerts',
        verbose_name=_('user')
    )
    name = models.CharField(_('alert name'), max_length=100)
    criteria = models.JSONField(_('search criteria'))
    active = models.BooleanField(_('active'), default=True)
    last_sent_at = models.DateTimeField(_('last sent at'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Alert')
        verbose_name_plural = _('Alerts')

    def __str__(self):
        return f"{self.user.email} - {self.name}"