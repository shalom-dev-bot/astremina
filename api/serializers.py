from rest_framework import serializers
from django.contrib.auth import get_user_model
from properties.models import Property, PropertyImage, Favorite, Alert
from partners.models import Partner, Contract
from accounts.models import Profile

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['photo', 'phone_number', 'preferred_language', 'ui_theme', 'bio']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_partner', 'date_joined', 'profile']
        read_only_fields = ['id', 'date_joined']

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'is_primary']

class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'slug', 'description', 'property_type', 'price', 'currency',
            'city', 'neighborhood', 'address', 'latitude', 'longitude', 'bedrooms',
            'bathrooms', 'surface_area', 'status', 'owner', 'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'owner', 'created_at', 'updated_at']

class PropertyListSerializer(serializers.ModelSerializer):
    """Serializer léger pour les listes"""
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'slug', 'property_type', 'price', 'currency',
            'city', 'neighborhood', 'latitude', 'longitude', 'primary_image', 'created_at'
        ]
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image.image.url
        first_image = obj.images.first()
        return first_image.image.url if first_image else None

class FavoriteSerializer(serializers.ModelSerializer):
    property = PropertyListSerializer(read_only=True)
    property_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'property', 'property_id', 'created_at']
        read_only_fields = ['id', 'created_at']

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['id', 'name', 'criteria', 'active', 'last_sent_at', 'created_at']
        read_only_fields = ['id', 'last_sent_at', 'created_at']

class PartnerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Partner
        fields = ['id', 'user', 'company_name', 'address', 'contact_email', 'contact_phone', 'created_at']
        read_only_fields = ['id', 'created_at']

class ContractSerializer(serializers.ModelSerializer):
    partner = PartnerSerializer(read_only=True)
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Contract
        fields = [
            'id', 'partner', 'start_date', 'end_date', 'status', 
            'max_publications', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']