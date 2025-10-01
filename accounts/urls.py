from django.urls import path
from . import views
from allauth.account.views import LogoutView

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.CustomSignupView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('', include('allauth.urls')),  # Routes Allauth (Google OAuth2, etc.)
]