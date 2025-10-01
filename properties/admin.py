from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Property, PropertyImage, Favorite, Alert

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'city', 'price', 'currency', 'status', 'owner', 'created_at')
    list_filter = ('property_type', 'status', 'city', 'created_at')
    search_fields = ('title', 'city', 'neighborhood', 'owner__email')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PropertyImageInline]
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'description', 'property_type', 'status')
        }),
        (_('Pricing'), {
            'fields': ('price', 'currency')
        }),
        (_('Location'), {
            'fields': ('city', 'neighborhood', 'address', 'latitude', 'longitude')
        }),
        (_('Details'), {
            'fields': ('bedrooms', 'bathrooms', 'surface_area')
        }),
        (_('Ownership & Source'), {
            'fields': ('owner', 'source', 'source_url')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('property__title',)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'property__title')

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'active', 'last_sent_at', 'created_at')
    list_filter = ('active', 'created_at')
    search_fields = ('user__email', 'name')