from django.urls import path
from . import views

app_name = 'scraping'

urlpatterns = [
    path('', views.scraping_source_list, name='source_list'),
    path('source/<int:source_id>/', views.scraping_source_detail, name='source_detail'),
    path('source/<int:source_id>/trigger/', views.trigger_scraping, name='trigger_scraping'),
]