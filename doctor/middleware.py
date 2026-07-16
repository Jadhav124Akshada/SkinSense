from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse, resolve
from django.urls.exceptions import Resolver404

class PortalRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Skip checks for static files, media, and unauthenticated users
        if not request.user.is_authenticated or request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)

        # 2. Skip security checks for the Django Admin site
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        # 3. Identify the current view name from the URL
        try:
            resolver_match = resolve(request.path_info)
            current_url_name = resolver_match.url_name
        except Resolver404:
            return self.get_response(request)

        # 4. Identify the user's role
        is_doctor = hasattr(request.user, 'doctor')

        # 5. Define Protected Lanes (Names must match your urls.py 'name=' attributes)
        doctor_only_views = ['dashboards', 'doctor_account', 'doctor_settings', 'doctor_patient_detail', 'doctor_mri_detail']
        patient_only_views = ['history', 'dashboard', 'mri', 'mid', 'NonMRI_Predict', 'MRI_Predict']

        # 6. Redirect Logic
        # If a Patient tries to access a Doctor view
        if current_url_name in doctor_only_views and not is_doctor:
            if current_url_name != 'index': 
                messages.error(request, "Access Denied: Doctors only.")
                return redirect('index')

        # If a Doctor tries to access a Patient view
        if current_url_name in patient_only_views and is_doctor:
            if current_url_name != 'dashboards':
                # Redirect back to doctor portal without an error message
                return redirect('dashboards')

        return self.get_response(request)
    