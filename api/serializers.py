from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from properties.models import Property, PropertyImage, Favorite
from partners.models import Partner, Contract
from accounts.models import Profile
from alerts.models import PropertyAlert

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
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'slug', 'description', 'property_type', 'price', 'currency',
            'city', 'neighborhood', 'address', 'latitude', 'longitude', 'bedrooms',
            'bathrooms', 'surface_area', 'status', 'owner', 'images', 'is_favorited',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'owner', 'created_at', 'updated_at']

    def get_is_favorited(self, obj):
        """Vérifie si la propriété est dans les favoris de l'utilisateur."""
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, property=obj).exists()
        return False

class PropertyListSerializer(serializers.ModelSerializer):
    """Serializer léger pour les listes"""
    primary_image = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'slug', 'property_type', 'price', 'currency',
            'city', 'neighborhood', 'latitude', 'longitude', 'primary_image',
            'is_favorited', 'created_at'
        ]
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image.image.url
        first_image = obj.images.first()
        return first_image.image.url if first_image else None
    
    def get_is_favorited(self, obj):
        """Vérifie si la propriété est dans les favoris de l'utilisateur."""
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, property=obj).exists()
        return False

class FavoriteSerializer(serializers.ModelSerializer):
    property = PropertyListSerializer(read_only=True)
    property_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'property', 'property_id', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_property_id(self, value):
        """Vérifie que la propriété existe et est publiée."""
        try:
            property = Property.objects.get(id=value, status='published')
        except Property.DoesNotExist:
            raise serializers.ValidationError(_('Property does not exist or is not published.'))
        return value

    def validate(self, data):
        """Vérifie que l'utilisateur n'a pas déjà mis cette propriété en favori."""
        user = self.context['request'].user
        property_id = data.get('property_id')
        if Favorite.objects.filter(user=user, property_id=property_id).exists():
            raise serializers.ValidationError(_('This property is already in your favorites.'))
        return data

    def create(self, validated_data):
        """Crée un favori avec l'utilisateur connecté."""
        property_id = validated_data.pop('property_id')
        property = Property.objects.get(id=property_id)
        return Favorite.objects.create(user=self.context['request'].user, property=property)

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