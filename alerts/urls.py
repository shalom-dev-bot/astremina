from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    path('create/', views.create_alert, name='create_alert'),
    path('edit/<int:alert_id>/', views.edit_alert, name='edit_alert'),
    path('delete/<int:alert_id>/', views.delete_alert, name='delete_alert'),
]