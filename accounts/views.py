from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import PatientRegistrationForm, UserLoginForm, UserProfileForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                    # Check next param
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('accounts:dashboard_redirect')
                else:
                    messages.error(request, "Your account has been deactivated. Please contact the administrator.")
            else:
                messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def register_patient_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account registered successfully! You can now log in to book appointments.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Please correct the errors in the registration form below.")
    else:
        form = PatientRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('accounts:login')


@login_required
def dashboard_redirect_view(request):
    user = request.user
    if user.is_admin_role:
        return redirect('dashboard:admin_dashboard')
    elif user.is_doctor_role:
        return redirect('doctors:doctor_dashboard')
    elif user.is_patient_role:
        return redirect('patients:patient_dashboard')
    else:
        # Fallback
        return redirect('home')


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'accounts/profile.html', {'form': form, 'user_obj': user})
