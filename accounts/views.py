from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from allauth.account.views import SignupView, LoginView
from allauth.socialaccount.models import SocialAccount
from .models import User, Profile
from .forms import ProfileForm  # À créer dans forms.py

class CustomSignupView(SignupView):
    template_name = 'account/signup.html'

class CustomLoginView(LoginView):
    template_name = 'account/login.html'

@login_required
def profile_view(request):
    """Vue pour afficher/modifier le profil utilisateur"""
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Profile updated successfully.'))
            return redirect('accounts:profile')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'account/profile.html', {
        'form': form,
        'profile': profile,
        'social_account': SocialAccount.objects.filter(user=request.user).first()
    })

@login_required
def logout_view(request):
    """Déconnexion de l'utilisateur"""
    logout(request)
    messages.success(request, _('You have been logged out.'))
    return redirect('properties:home')