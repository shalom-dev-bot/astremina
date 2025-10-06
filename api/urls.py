from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    UserViewSet, PropertyViewSet, FavoriteViewSet, 
    AlertViewSet, PartnerViewSet, ContractViewSet,
    DashboardStatsView, ScrapingControlView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'partners', PartnerViewSet, basename='partner')
router.register(r'contracts', ContractViewSet, basename='contract')

urlpatterns = [
    # Authentication
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints
    path('', include(router.urls)),
    
    # Dashboard & Stats
    path('dashboard/summary/', DashboardStatsView.as_view(), name='dashboard_summary'),
    
    # Scraping control
    path('scraper/run/', ScrapingControlView.as_view(), name='scraper_run'),
]