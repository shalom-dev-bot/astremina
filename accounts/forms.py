from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'phone_number', 'preferred_language', 'ui_theme', 'bio']
        labels = {
            'photo': _('Profile Photo'),
            'phone_number': _('Phone Number'),
            'preferred_language': _('Preferred Language'),
            'ui_theme': _('UI Theme'),
            'bio': _('Bio'),
        }
        widgets = {
            'photo': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500',
                'placeholder': _('Enter phone number')
            }),
            'preferred_language': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500'
            }),
            'ui_theme': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500',
                'rows': 4,
                'placeholder': _('Tell us about yourself')
            }),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.replace('+', '').replace(' ', '').isdigit():
            raise forms.ValidationError(_('Phone number must contain only digits and optional + prefix.'))
        return phone_number

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError(_('Photo size must not exceed 5MB.'))
            valid_types = ['image/jpeg', 'image/png']
            if photo.content_type not in valid_types:
                raise forms.ValidationError(_('Only JPEG and PNG images are allowed.'))
        return photo