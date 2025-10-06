from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import PropertyAlert

class PropertyAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyAlert
        fields = [
            'id', 'name', 'city', 'property_type', 'min_price', 'max_price',
            'min_bedrooms', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Validation cohérente avec le form."""
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            raise serializers.ValidationError(_('Minimum price cannot be greater than maximum price.'))
        
        if min_price and min_price < 0:
            raise serializers.ValidationError(_('Minimum price cannot be negative.'))
        
        if max_price and max_price < 0:
            raise serializers.ValidationError(_('Maximum price cannot be negative.'))
        
        if data.get('min_bedrooms') and data.get('min_bedrooms') < 0:
            raise serializers.ValidationError(_('Minimum bedrooms cannot be negative.'))
        
        return data

    def create(self, validated_data):
        """Crée l'alerte avec l'utilisateur connecté."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)