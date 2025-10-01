from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Property, PropertyImage

class PropertySearchForm(forms.Form):
    city = forms.CharField(
        label=_('City'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent',
            'placeholder': _('Enter city name...')
        })
    )
    
    property_type = forms.ChoiceField(
        label=_('Property Type'),
        choices=[('', _('All Types'))] + Property.PROPERTY_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent'
        })
    )
    
    min_price = forms.DecimalField(
        label=_('Min Price'),
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent',
            'placeholder': _('Min price')
        })
    )
    
    max_price = forms.DecimalField(
        label=_('Max Price'),
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent',
            'placeholder': _('Max price')
        })
    )
    
    bedrooms = forms.IntegerField(
        label=_('Bedrooms'),
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent',
            'placeholder': _('Number of bedrooms')
        })
    )

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'property_type', 'price', 'currency',
            'city', 'neighborhood', 'address', 'latitude', 'longitude'
        ]
        labels = {
            'title': _('Title'),
            'description': _('Description'),
            'property_type': _('Property Type'),
            'price': _('Price'),
            'currency': _('Currency'),
            'city': _('City'),
            'neighborhood': _('Neighborhood'),
            'address': _('Address'),
            'latitude': _('Latitude'),
            'longitude': _('Longitude'),
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500', 'rows': 4}),
            'property_type': forms.Select(attrs={'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500', 'step': '0.01'}),
            'currency': forms.Select(attrs={'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500'}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500'}),
            'neighborhood': forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500'}),
            'address': forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500'}),
            'latitude': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500', 'step': '0.000001'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError(_('Price cannot be negative.'))
        return price

    def clean_latitude(self):
        latitude = self.cleaned_data.get('latitude')
        if latitude is not None and (latitude < -90 or latitude > 90):
            raise forms.ValidationError(_('Latitude must be between -90 and 90.'))
        return latitude

    def clean_longitude(self):
        longitude = self.cleaned_data.get('longitude')
        if longitude is not None and (longitude < -180 or longitude > 180):
            raise forms.ValidationError(_('Longitude must be between -180 and 180.'))
        return longitude

class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image', 'is_primary']
        labels = {
            'image': _('Image'),
            'is_primary': _('Primary Image'),
        }
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-red-500 focus:ring-red-500 border-gray-700 rounded'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError(_('Image size must not exceed 5MB.'))
            valid_types = ['image/jpeg', 'image/png']
            if image.content_type not in valid_types:
                raise forms.ValidationError(_('Only JPEG and PNG images are allowed.'))
        return image