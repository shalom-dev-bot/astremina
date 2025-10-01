from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.home, name='home'),
    path('properties/', views.property_list, name='list'),
    path('property/<slug:slug>/', views.property_detail, name='detail'),
    path('map/', views.map_view, name='map'),
    path('favorites/', views.favorites, name='favorites'),
    path('create/', views.property_create, name='create'),
    path('property/<slug:slug>/edit/', views.property_edit, name='edit'),
    path('property/<slug:slug>/delete/', views.property_delete, name='delete'),
]