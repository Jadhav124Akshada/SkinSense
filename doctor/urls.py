from django.urls import path
from doctor import views

urlpatterns = [
    # --- Dashboard ---
    path('dashboards', views.dashboards, name='dashboards'),

    # --- Authentication ---
    path("doctor_register", views.doctor_register, name="doctor_register"),    
    path("doctor_login", views.doctor_login, name="doctor_login"),    
    
    # ✅ CORRECTED LOGOUT (Removes the broken 'log_out' line)
    path("doctor/logout/", views.doctor_logout, name="doctor_logout"),

    # --- Detail Views ---
    path('patient_detail/<int:id>/', views.doctor_patient_detail, name='doctor_patient_detail'),
    path('mri_detail/<int:id>/', views.doctor_mri_detail, name='doctor_mri_detail'),
    # --- Account & Settings ---
    # These match the names used in your sidebar links in dashboards.html
    path('doctor_account/', views.doctor_account, name='doctor_account'),
    path('doctor_settings/', views.doctor_settings, name='doctor_settings'),

    # --- Other ---
    path("index1", views.index1, name="index1"), 
    
       
]