from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('', views.log_in, name='log_in'),
    
    # Authentication
    path('log_in', views.log_in, name='log_in'),
    path('register', views.register, name='register'),
    path('log_out/', views.log_out, name='log_out'), # Fixed: Removed .html from name
    path('history/', views.history, name='history'),
    path('account/', views.account, name='account'),
    path('settings/', views.settings, name='settings'),

    # Dashboard & Navigation
    path('index/', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),

    # AI Predictions (The ML Engineer's work)
    path('mri', views.mri, name='mri'),
    path('mid', views.mid, name='mid'),
    path('MRI_Predict', views.MRI_Predict, name='MRI_Predict'),
    path('NonMRI_Predict', views.NonMRI_Predict, name='NonMRI_Predict'),

    # Appointments & PDF Reports (The Database work)
    path('book_appointment/', views.book_appointment, name='book_appointment'),
    path('book_mri_appointment/', views.book_mri_appointment, name='book_mri_appointment'),
    path("appointment_result/<int:patient_id>/", views.appointment_result, name="appointment_result"),
    path('mri_appointment_result/<int:patient_id>/', views.mri_appointment_result, name='mri_appointment_result'),
    path('download-pdf/<int:patient_id>/', views.download_pdf, name='download_pdf'),
    path('download-pdf-mri/<int:patient_id>/', views.download_pdf_mri, name='download_pdf_mri'),

    # Features
    path("chatbot_api/", views.chatbot_api, name="chatbot_api"),
    path('download_pdf_mri/<int:patient_id>/', views.download_pdf_mri, name='download_pdf_mri'),

    # Delete URLs
    path('delete-mri/<int:record_id>/', views.delete_mri, name='delete_mri'),
    path('delete-symptom/<int:record_id>/', views.delete_symptom, name='delete_symptom'),
    
    path('history/bulk-delete-mri/', views.bulk_delete_mri, name='bulk_delete_mri'),
path('history/bulk-delete-symptoms/', views.bulk_delete_symptoms, name='bulk_delete_symptoms'),
  
    
]