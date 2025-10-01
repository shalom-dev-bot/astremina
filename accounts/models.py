from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    is_partner = models.BooleanField(_('is partner'), default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

class Profile(models.Model):
    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('fr', _('Français')),
    ]
    
    THEME_CHOICES = [
        ('dark', _('Dark')),
        ('light', _('Light')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(_('photo'), upload_to='profiles/', blank=True, null=True)
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    preferred_language = models.CharField(
        _('preferred language'), 
        max_length=2, 
        choices=LANGUAGE_CHOICES, 
        default='en'
    )
    ui_theme = models.CharField(
        _('UI theme'), 
        max_length=5, 
        choices=THEME_CHOICES, 
        default='dark'
    )
    bio = models.TextField(_('bio'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email}'s profile"