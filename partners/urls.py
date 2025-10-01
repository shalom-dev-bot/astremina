from django.urls import path
from . import views

app_name = 'partners'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('properties/', views.my_properties, name='my_properties'),
]