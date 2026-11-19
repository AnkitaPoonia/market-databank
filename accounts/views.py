from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from .forms import UserRegistrationForm, UserLoginForm, UserProfileUpdateForm

def register_view(request):
    """
    Handle user registration with form validation and password encryption.
    """
    if request.user.is_authenticated:
        return redirect('databank:dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created successfully for {user.username}! You can now log in.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'hide_sidebar': True,
    })


def login_view(request):
    """
    Handle user login with session control and credentials verification.
    """
    if request.user.is_authenticated:
        return redirect('databank:dashboard')

    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # Session expiry based on 'Remember Me'
                    if not remember_me:
                        request.session.set_expiry(0)  # Expires when browser closes
                    else:
                        request.session.set_expiry(1209600)  # 2 weeks in seconds

                    messages.success(request, f"Welcome back, {user.username}!")

                    # Safe redirect validation
                    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                        return redirect(next_url)
                    return redirect('databank:dashboard')
                else:
                    messages.error(request, "This account is currently inactive. Please contact the administrator.")
            else:
                messages.error(request, "Invalid username or password. Please try again.")
        else:
            messages.error(request, "Please enter both username and password.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'next': next_url,
        'hide_sidebar': True,
    })


def logout_view(request):
    """
    Handle user logout and flush the session safely.
    """
    if request.method == 'POST':
        logout(request)
        messages.info(request, "You have been logged out securely. See you next time!")
        return redirect('accounts:login')
    
    # If accessed via GET, render a simple confirmation or redirect
    logout(request)
    messages.info(request, "You have been logged out securely.")
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """
    Display and update user profile information, showing dataset activity statistics.
    """
    from databank.models import MarketData
    from sharing.models import DataShare

    created_count = MarketData.objects.filter(created_by=request.user).count()
    shared_by_user_count = DataShare.objects.filter(shared_by=request.user, is_active=True).count()
    shared_with_user_count = DataShare.objects.filter(shared_with=request.user, is_active=True).count()

    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=request.user, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been updated successfully.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the errors in the profile form.")
    else:
        form = UserProfileUpdateForm(instance=request.user, user=request.user)

    context = {
        'form': form,
        'created_count': created_count,
        'shared_by_user_count': shared_by_user_count,
        'shared_with_user_count': shared_with_user_count,
    }
    return render(request, 'accounts/profile.html', context)
