from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

app_name = 'alerts'

# Router pour l'API
router = DefaultRouter()
router.register(r'api/alerts', views.AlertViewSet, basename='alert')

urlpatterns = [
    # Vues basées sur templates
    path('', views.list_alerts, name='list_alerts'),
    path('create/', views.create_alert, name='create_alert'),
    path('edit/<int:alert_id>/', views.edit_alert, name='edit_alert'),
    path('delete/<int:alert_id>/', views.delete_alert, name='delete_alert'),
    # Routes API
    path('', include(router.urls)),
]