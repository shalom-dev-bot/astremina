from django import forms
from django.utils.translation import gettext_lazy as _
from .models import PropertyAlert

class PropertyAlertForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        label=_('Alert Name'),
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full pl-10 pr-4 py-3 bg-netflix-gray border border-netflix-light-gray rounded-lg text-white placeholder-netflix-light-gray focus:outline-none focus:ring-2 focus:ring-netflix-red',
            'placeholder': _('e.g., My Dream Home Alert')
        })
    )

    class Meta:
        model = PropertyAlert
        fields = ['name', 'city', 'property_type', 'min_price', 'max_price', 'min_bedrooms', 'is_active']
        widgets = {
            'city': forms.TextInput(attrs={
                'class': 'form-input w-full pl-10 pr-4 py-3 bg-netflix-gray border border-netflix-light-gray rounded-lg text-white placeholder-netflix-light-gray focus:outline-none focus:ring-2 focus:ring-netflix-red',
                'placeholder': _('e.g., Douala')
            }),
            'property_type': forms.Select(choices=[
                ('', _('Any')),
                ('house', _('House')),
                ('apartment', _('Apartment')),
                ('land', _('Land')),
                ('hotel', _('Hotel')),
            ], attrs={
                'class': 'form-select w-full pl-10 pr-4 py-3 bg-netflix-gray border border-netflix-light-gray rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-netflix-red'
            }),
            'min_price': forms.NumberInput(attrs={
                'class': 'form-input w-full pl-10 pr-4 py-3 bg-netflix-gray border border-netflix-light-gray rounded-lg text-white placeholder-netflix-light-gray focus:outline-none focus:ring-2 focus:ring-netflix-red',
                'placeholder': '0'
            }),
            'max_price': forms.NumberInput(attrs={
                'class': 'form-input w-full pl-10 pr-4 py-3 bg-netflix-gray border border-netflix-light-gray rounded-lg text-white placeholder-netflix-light-gray focus:outline-none focus:ring-2 focus:ring-netflix-red',
                'placeholder': '1000000'
            }),
            'min_bedrooms': forms.NumberInput(attrs={
                'class': 'form-input w-full pl-10 pr-4 py-3 bg-netflix-gray border border-netflix-light-gray rounded-lg text-white placeholder-netflix-light-gray focus:outline-none focus:ring-2 focus:ring-netflix-red',
                'placeholder': '1'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-netflix-red bg-netflix-gray border-netflix-light-gray rounded focus:ring-netflix-red'
            }),
        }
        labels = {
            'name': _('Alert Name'),
            'city': _('City'),
            'property_type': _('Property Type'),
            'min_price': _('Minimum Price'),
            'max_price': _('Maximum Price'),
            'min_bedrooms': _('Minimum Bedrooms'),
            'is_active': _('Active'),
        }

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            raise forms.ValidationError(_('Minimum price cannot be greater than maximum price.'))
        
        if min_price and min_price < 0:
            raise forms.ValidationError(_('Minimum price cannot be negative.'))
        
        if max_price and max_price < 0:
            raise forms.ValidationError(_('Maximum price cannot be negative.'))
        
        if cleaned_data.get('min_bedrooms') and cleaned_data.get('min_bedrooms') < 0:
            raise forms.ValidationError(_('Minimum bedrooms cannot be negative.'))
        
        return cleaned_data