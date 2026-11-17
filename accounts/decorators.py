from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


def role_required(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this page.")
                return redirect('accounts:login')

            user_role = getattr(request.user, 'role', None)
            is_admin = request.user.is_superuser or request.user.is_staff or user_role == 'ADMIN'

            if 'ADMIN' in allowed_roles and is_admin:
                return view_func(request, *args, **kwargs)

            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)

            messages.error(request, "You do not have permission to access that page.")
            return redirect('accounts:dashboard_redirect')
        return _wrapped_view
    return decorator


def patient_required(view_func):
    return role_required(['PATIENT'])(view_func)


def doctor_required(view_func):
    return role_required(['DOCTOR'])(view_func)


def admin_required(view_func):
    return role_required(['ADMIN'])(view_func)
