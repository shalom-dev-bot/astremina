from django import forms
from django.utils.translation import gettext_lazy as _
from .models import PropertyAlert

class PropertyAlertForm(forms.ModelForm):
    class Meta:
        model = PropertyAlert
        fields = ['city', 'property_type', 'min_price', 'max_price', 'min_bedrooms', 'is_active']
        widgets = {
            'city': forms.TextInput(attrs={'class': 'form-input mt-1 block w-full'}),
            'property_type': forms.Select(choices=[
                ('', _('Any')),
                ('house', _('House')),
                ('apartment', _('Apartment')),
                ('land', _('Land')),
                ('hotel', _('Hotel')),
            ], attrs={'class': 'form-select mt-1 block w-full'}),
            'min_price': forms.NumberInput(attrs={'class': 'form-input mt-1 block w-full'}),
            'max_price': forms.NumberInput(attrs={'class': 'form-input mt-1 block w-full'}),
            'min_bedrooms': forms.NumberInput(attrs={'class': 'form-input mt-1 block w-full'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox mt-1'}),
        }
        labels = {
            'city': _('City'),
            'property_type': _('Property Type'),
            'min_price': _('Minimum Price'),
            'max_price': _('Maximum Price'),
            'min_bedrooms': _('Minimum Bedrooms'),
            'is_active': _('Active'),
        }