import os
import json
import base64
import random
from httpx import request
import joblib
import numpy as np
import tensorflow as tf
import google.generativeai as genai
import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings as conf

# --- ReportLab Imports ---
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from .auth import authentication 
from doctor.models import Doctor
from .forms import skin_symptom_form
from .models import PatientSkinData, MRIPatientData , Doctor
from .models import ContactMessage 
from django.conf import settings
from django.http import HttpResponse
from django.core.files.base import ContentFile

# ✅ NEW: Import Ultralytics YOLO for the new model
from ultralytics import YOLO
from PIL import Image  # For handling images in YOLO prediction

# ---------------------------------------------------------
# CONSTANTS & DATA MAPPINGS
# ---------------------------------------------------------

SYMPTOM_INDEX_MAP = {
    "0": "Itching", "1": "Redness", "2": "Rash", "3": "Scaling",
    "4": "Blister", "5": "Pus Filled", "6": "Pain", "7": "Dry Skin",
    "8": "Swelling", "9": "Burning", "10": "Cracks", "11": "Circular Rash",
    "12": "Oozing", "13": "Fever", "14": "Hair Loss", "15": "Dark Spot",
    "16": "Numbness", "17": "Ulcer", "18": "Peeling", "19": "Thickness"
}
# ---------------------------------------------------------
# FINAL DOCTORS DATA (ONLY PROVIDED SANGAMNER SPECIALISTS)
# ---------------------------------------------------------
DOCTORS_DATA = [
    {"disease": "Rosacea", "doctors": [
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Orange Corner, Suyog Colony, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"},
        {"name": "Dr. Neha Pagdal", "specialization": "Dermatologist", "location": "2nd floor, Shree Bungalow, Tajane Mala, near Jathar hospital, Sangamner, Maharashtra 422605", "contact": "+91 95612 15236", "email": "neha@gmail.com"},
        {"name": "Dr. Sachala Aniket Kasar", "specialization": "Cosmetologist", "location": "1st floor, Kamal Kedar complex, Janata Raja Marg, Sangamner, Maharashtra 422605", "contact": "+91 70307 04664", "email": "sachala@gmail.com"}
    ]},
    {"disease": "Vitiligo", "doctors": [
        {"name": "Dr. Neha Pagdal", "specialization": "Skin Specialist", "location": "2nd floor, Shree Bungalow, Tajane Mala, near Jathar hospital, Sangamner, Maharashtra 422605", "contact": "+91 95612 15236", "email": "neha@gmail.com"},
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Orange Corner, Suyog Colony, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"},
        {"name": "Dr. Sham Sangoram", "specialization": "Dermatologist", "location": "Link Rd, Bagvan Pura, Sangamner, Maharashtra 422605", "contact": "+91 2425 224 974", "email": "sangoram@gmail.com"}
    ]},
    {"disease": "Impetigo", "doctors": [
        {"name": "Dr. Varsha Hone", "specialization": "Skin Specialist", "location": "Tajane mala, near Adhaar blood bank, Bagvan Pura, Sangamner, Maharashtra 422605", "contact": "+91 73832 08043", "email": "varsha@gmail.com"},
        {"name": "Dr. Sachala Aniket Kasar", "specialization": "Dermatologist", "location": "1st floor, Skincare clinic Kamal Kedar complex, Sangamner, Maharashtra 422605", "contact": "+91 70307 04664", "email": "sachala@gmail.com"},
        {"name": "Dr. Neha Pagdal", "specialization": "Dermatologist", "location": "2nd floor, Shree Bungalow, near Jathar hospital, Sangamner, Maharashtra 422605", "contact": "+91 95612 15236", "email": "neha@gmail.com"}
    ]},
    {"disease": "Scabies", "doctors": [
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Orange Corner, Suyog Colony, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"},
        {"name": "Dr. Anil Joshi", "specialization": "Medical Clinic", "location": "H6C6+55G, Link Rd, Bagvan Pura, Sangamner, Maharashtra 422605", "contact": "+91 98234 56789", "email": "anil@gmail.com"},
        {"name": "Dr. Sham Sangoram", "specialization": "Skin Specialist", "location": "Link Rd, Bagvan Pura, Sangamner, Maharashtra 422605", "contact": "+91 2425 224 974", "email": "sangoram@gmail.com"}
    ]},
    {"disease": "Acne", "doctors": [
        {"name": "Dr. Neha Pagdal", "specialization": "Skin & Hair Specialist", "location": "2nd floor, Shree Bungalow, Tajane Mala, near Jathar hospital, Sangamner, Maharashtra 422605", "contact": "+91 95612 15236", "email": "neha@gmail.com"},
        {"name": "Dr. Sachala Aniket Kasar", "specialization": "Dermatologist", "location": "1st floor, Skincare clinic Kamal Kedar complex, Sangamner, Maharashtra 422605", "contact": "+91 70307 04664", "email": "sachala@gmail.com"},
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Orange Corner, Suyog Colony, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"}
    ]},
    {"disease": "Shingles", "doctors": [
        {"name": "Dr. Sham Sangoram", "specialization": "Dermatologist", "location": "Link Rd, Bagvan Pura, Sangamner, Maharashtra 422605", "contact": "+91 2425 224 974", "email": "sangoram@gmail.com"},
        {"name": "Dr. Varsha Hone", "specialization": "Skin Specialist", "location": "Tajane mala, near Adhaar blood bank, Sangamner, Maharashtra 422605", "contact": "+91 73832 08043", "email": "varsha@gmail.com"},
        {"name": "Dr. Neha Pagdal", "specialization": "Dermatologist", "location": "2nd floor, Shree Bungalow, Tajane Mala, near Jathar hospital, Sangamner, Maharashtra 422605", "contact": "+91 95612 15236", "email": "neha@gmail.com"}
    ]},
    {"disease": "Melanoma", "doctors": [
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Orange Corner, Suyog Colony, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"},
        {"name": "Dr. Neha Pagdal", "specialization": "Dermatologist", "location": "2nd floor, Shree Bungalow, Tajane Mala, near Jathar hospital, Sangamner, Maharashtra 422605", "contact": "+91 95612 15236", "email": "neha@gmail.com"},
        {"name": "Dr. Sham Sangoram", "specialization": "Oncology Skin Expert", "location": "Link Rd, Bagvan Pura, Sangamner, Maharashtra 422605", "contact": "+91 2425 224 974", "email": "sangoram@gmail.com"}
    ]},
    {"disease": "Psoriasis", "doctors": [
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Orange Corner, Suyog Colony, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"},
        {"name": "Dr. Neha Pagdal", "specialization": "Skin Specialist", "location": "2nd floor, Shree Bungalow, Tajane Mala, near Jathar hospital, Sangamner, Maharashtra 422605", "contact": "+91 95612 15236", "email": "neha@gmail.com"},
        {"name": "Dr. Sham Sangoram", "specialization": "Dermatologist", "location": "Link Rd, Bagvan Pura, Sangamner, Maharashtra 422605", "contact": "+91 2425 224 974", "email": "sangoram@gmail.com"}
    ]},
    {"disease": "Eczema", "doctors": [
        {"name": "Dr. Sachala Aniket Kasar", "specialization": "Dermatologist", "location": "1st floor, Skincare clinic Kamal Kedar complex, Janata Raja Marg, Sangamner, Maharashtra 422605", "contact": "+91 70307 04664", "email": "sachala@gmail.com"},
        {"name": "Dr. Neha Pagdal", "specialization": "Dermatologist", "location": "2nd floor, Shree Bungalow, near Jathar hospital, Sangamner, Maharashtra 422605", "contact": "+91 95612 15236", "email": "neha@gmail.com"},
        {"name": "Dr. Varsha Hone", "specialization": "Skin Specialist", "location": "Tajane mala, Bagvan Pura, Sangamner, Maharashtra 422605", "contact": "+91 73832 08043", "email": "varsha@gmail.com"}
    ]},
    {"disease": "Ringworm", "doctors": [
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Orange Corner, Suyog Colony, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"},
        {"name": "Dr. Sham Sangoram", "specialization": "Dermatologist", "location": "Link Rd, Bagvan Pura, Sangamner, Maharashtra 422605", "contact": "+91 2425 224 974", "email": "sangoram@gmail.com"},
        {"name": "Dr. Sachala Aniket Kasar", "specialization": "Skin Specialist", "location": "1st floor, Skincare clinic Kamal Kedar complex, Sangamner, Maharashtra 422605", "contact": "+91 70307 04664", "email": "sachala@gmail.com"}
    ]},
    {"disease": "Actinic Keratosis", "doctors": [
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Orange Corner, Suyog Colony, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"},
        {"name": "Dr. Neha Pagdal", "specialization": "Dermatologist", "location": "2nd floor, Shree Bungalow, Tajane Mala, near Jathar hospital, Sangamner, Maharashtra 422605", "contact": "+91 95612 15236", "email": "neha@gmail.com"},
        {"name": "Dr. Anil Joshi", "specialization": "Medical Clinic", "location": "Link Rd, Bagvan Pura, Sangamner, Maharashtra 422605", "contact": "+91 98234 56789", "email": "anil@gmail.com"}
    ]},
    {"disease": "Basal Cell Carcinoma", "doctors": [
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Orange Corner, Suyog Colony, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"},
        {"name": "Dr. Varsha Hone", "specialization": "Skin Specialist", "location": "Tajane mala, near Adhaar blood bank, Bagvan Pura, Sangamner, Maharashtra 422605", "contact": "+91 73832 08043", "email": "varsha@gmail.com"},
        {"name": "Dr. Sham Sangoram", "specialization": "Dermatologist", "location": "Link Rd, Bagvan Pura, Sangamner, Maharashtra 422605", "contact": "+91 2425 224 974", "email": "sangoram@gmail.com"}
    ]},
    {"disease": "Chickenpox", "doctors": [
        {"name": "Dr. Varsha Hone", "specialization": "Skin Specialist", "location": "Tajane mala, near Adhaar blood bank, Sangamner, Maharashtra 422605", "contact": "+91 73832 08043", "email": "varsha@gmail.com"},
        {"name": "Dr. Anil Joshi", "specialization": "General Physician", "location": "Link Rd, Bagvan Pura, Sangamner, Maharashtra 422605", "contact": "+91 98234 56789", "email": "anil@gmail.com"},
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"}
    ]},
    {"disease": "Dermato Fibroma", "doctors": [
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Orange Corner, Suyog Colony, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"},
        {"name": "Dr. Neha Pagdal", "specialization": "Skin Specialist", "location": "2nd floor, Shree Bungalow, Tajane Mala, near Jathar hospital, Sangamner, Maharashtra 422605", "contact": "+91 95612 15236", "email": "neha@gmail.com"},
        {"name": "Dr. Sachala Aniket Kasar", "specialization": "Cosmetologist", "location": "Kamal Kedar complex, Sangamner, Maharashtra 422605", "contact": "+91 70307 04664", "email": "sachala@gmail.com"}
    ]},
    {"disease": "Dyshidrotic Eczema", "doctors": [
        {"name": "Dr. Sachala Aniket Kasar", "specialization": "Dermatologist", "location": "1st floor, Skincare clinic Kamal Kedar complex, Sangamner, Maharashtra 422605", "contact": "+91 70307 04664", "email": "sachala@gmail.com"},
        {"name": "Dr. Neha Pagdal", "specialization": "Dermatologist", "location": "2nd floor, Shree Bungalow, Tajane Mala, Sangamner, Maharashtra 422605", "contact": "+91 95612 15236", "email": "neha@gmail.com"},
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"}
    ]},
    {"disease": "Nail Fungus", "doctors": [
        {"name": "Dr. Neha Pagdal", "specialization": "Skin Specialist", "location": "2nd floor, Shree Bungalow, Tajane Mala, near Jathar hospital, Sangamner, Maharashtra 422605", "contact": "+91 95612 15236", "email": "neha@gmail.com"},
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Orange Corner, Suyog Colony, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"},
        {"name": "Dr. Sachala Aniket Kasar", "specialization": "Cosmetologist", "location": "1st floor, Skincare clinic Kamal Kedar complex, Sangamner, Maharashtra 422605", "contact": "+91 70307 04664", "email": "sachala@gmail.com"}
    ]},
    {"disease": "Nevus", "doctors": [
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Orange Corner, Suyog Colony, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"},
        {"name": "Dr. Neha Pagdal", "specialization": "Skin Specialist", "location": "2nd floor, Shree Bungalow, Tajane Mala, near Jathar hospital, Sangamner, Maharashtra 422605", "contact": "+91 95612 15236", "email": "neha@gmail.com"},
        {"name": "Dr. Sham Sangoram", "specialization": "Dermatologist", "location": "Link Rd, Bagvan Pura, Sangamner, Maharashtra 422605", "contact": "+91 2425 224 974", "email": "sangoram@gmail.com"}
    ]},
    {"disease": "Normal Skin", "doctors": [
        {"name": "Dr. Sachala Aniket Kasar", "specialization": "Skin Care Expert", "location": "1st floor, Skincare clinic Kamal Kedar complex, Sangamner, Maharashtra 422605", "contact": "+91 70307 04664", "email": "sachala@gmail.com"},
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Orange Corner, Suyog Colony, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"},
        {"name": "Dr. Varsha Hone", "specialization": "Cosmetologist", "location": "Tajane mala, Sangamner, Maharashtra 422605", "contact": "+91 73832 08043", "email": "varsha@gmail.com"}
    ]},
    {"disease": "Pigmented Benign Keratosis", "doctors": [
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Orange Corner, Suyog Colony, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"},
        {"name": "Dr. Neha Pagdal", "specialization": "Skin Specialist", "location": "2nd floor, Shree Bungalow, near Jathar hospital, Sangamner, Maharashtra 422605", "contact": "+91 95612 15236", "email": "neha@gmail.com"},
        {"name": "Dr. Sham Sangoram", "specialization": "Dermatologist", "location": "Link Rd, Bagvan Pura, Sangamner, Maharashtra 422605", "contact": "+91 2425 224 974", "email": "sangoram@gmail.com"}
    ]},
    {"disease": "Seborrheic Keratosis", "doctors": [
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Orange Corner, Suyog Colony, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"},
        {"name": "Dr. Neha Pagdal", "specialization": "Dermatologist", "location": "2nd floor, Shree Bungalow, Tajane Mala, Sangamner, Maharashtra 422605", "contact": "+91 95612 15236", "email": "neha@gmail.com"},
        {"name": "Dr. Sachala Aniket Kasar", "specialization": "Cosmetologist", "location": "Kamal Kedar complex, Janata Raja Marg, Sangamner, Maharashtra 422605", "contact": "+91 70307 04664", "email": "sachala@gmail.com"}
    ]},
    {"disease": "Squamous Cell Carcinoma", "doctors": [
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Orange Corner, Suyog Colony, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"},
        {"name": "Dr. Varsha Hone", "specialization": "Skin Specialist", "location": "Tajane mala, near Adhaar blood bank, Bagvan Pura, Sangamner, Maharashtra 422605", "contact": "+91 73832 08043", "email": "varsha@gmail.com"},
        {"name": "Dr. Sham Sangoram", "specialization": "Onco-Dermatologist", "location": "Link Rd, Bagvan Pura, Sangamner, Maharashtra 422605", "contact": "+91 2425 224 974", "email": "sangoram@gmail.com"}
    ]},
    {"disease": "Vascular Lesion", "doctors": [
        {"name": "Dr. Pravin Dayama", "specialization": "Dermatologist", "location": "Kaushalyam Building, Orange Corner, Suyog Colony, Sangamner, Maharashtra 422605", "contact": "+91 90498 84354", "email": "dayama@gmail.com"},
        {"name": "Dr. Sachala Aniket Kasar", "specialization": "Skin Specialist", "location": "1st floor, Skincare clinic Kamal Kedar complex, Sangamner, Maharashtra 422605", "contact": "+91 70307 04664", "email": "sachala@gmail.com"},
        {"name": "Dr. Neha Pagdal", "specialization": "Dermatologist", "location": "Tajane Mala, Sangamner, Maharashtra 422605", "contact": "+91 95612 15236", "email": "neha@gmail.com"}
    ]}
]
PRECAUTIONS_DATA =[
    {"disease": "Acne", "precautions": ["Wash face twice daily", "Avoid touching face", "Stay hydrated"]},
    {"disease": "Actinic Keratosis", "precautions": ["Apply sunscreen daily", "Wear protective hats"]},
    {"disease": "Basal Cell Carcinoma", "precautions": ["Use SPF 50+ sunscreen", "Wear protective clothing", "Consult oncologist"]},
    {"disease": "Chickenpox", "precautions": ["Isolate to prevent spread", "Do not scratch blisters"]},
    {"disease": "Dermato Fibroma", "precautions": ["Monitor for size changes", "Consult if painful"]},
    {"disease": "Dyshidrotic Eczema", "precautions": ["Keep hands/feet dry", "Use fragrance-free moisturizers"]},
    {"disease": "Melanoma", "precautions": ["Avoid direct sun exposure", "Regular skin checks"]},
    {"disease": "Nail Fungus", "precautions": ["Keep nails dry and clean", "Do not share nail clippers"]},
    {"disease": "Nevus", "precautions": ["Monitor ABCD (Asymmetry, Border, Color, Diameter)", "Protect from sun"]},
    {"disease": "Normal Skin", "precautions": ["Maintain daily hygiene", "Use sunscreen"]},
    {"disease": "Pigmented Benign Keratosis", "precautions": ["Protect from sun", "Monitor for rapid growth"]},
    {"disease": "Ringworm", "precautions": ["Keep area clean and dry", "Don't share towels"]},
    {"disease": "Seborrheic Keratosis", "precautions": ["Do not scratch or pick", "Protect from sun"]},
    {"disease": "Squamous Cell Carcinoma", "precautions": ["Strict sun avoidance", "Protective clothing"]},
    {"disease": "Vascular Lesion", "precautions": ["Avoid trauma to area", "Monitor for bleeding"]},
    {"disease": "Rosacea", "precautions": ["Avoid spicy foods", "Use gentle cleansers", "Protect from sun"]},
    {"disease": "Vitiligo", "precautions": ["Use high SPF sunscreen", "Manage stress"]},
    {"disease": "Impetigo", "precautions": ["Keep sores covered", "Wash hands frequently"]},
    {"disease": "Scabies", "precautions": ["Wash all bedding in hot water", "Treat all household members"]},
    {"disease": "Shingles", "precautions": ["Keep rash covered", "Avoid pregnant women"]},
    {"disease": "Psoriasis", "precautions": ["Moisturize daily", "Manage stress"]},
    {"disease": "Eczema", "precautions": ["Moisturize frequently", "Avoid triggers"]}
]

PRODUCTS_DATA = {
  "Acne": [
      {"name": "Salicylic Acid Face Wash", "link": "https://www.amazon.in/s?k=salicylic+acid+face+wash"},
      {"name": "Benzoyl Peroxide Gel", "link": "https://www.1mg.com/search/all?name=Benzoyl%20Peroxide"},
      {"name": "Oil-Free Moisturizer", "link": "https://www.amazon.in/s?k=oil+free+moisturizer"}
  ],
  "Actinic Keratosis": [
      {"name": "Sunscreen SPF 50+", "link": "https://www.amazon.in/s?k=sunscreen+spf+50"},
      {"name": "Aloe Vera Gel", "link": "https://www.amazon.in/s?k=aloe+vera+gel"},
      {"name": "Vitamin C Serum", "link": "https://www.amazon.in/s?k=vitamin+c+serum"}
  ],
  "Basal Cell Carcinoma": [
      {"name": "SPF 50+ Sunscreen", "link": "https://www.amazon.in/s?k=spf+50+sunscreen"},
      {"name": "Protective Clothing", "link": "https://www.amazon.in/s?k=uv+protection+clothing"},
      {"name": "Vitamin E Cream", "link": "https://www.1mg.com/otc/vitamin-e-cream-otc"}
  ],
  "Chickenpox": [
      {"name": "Calamine Lotion", "link": "https://www.amazon.in/s?k=calamine+lotion"},
      {"name": "Oatmeal Bath Powder", "link": "https://www.amazon.in/s?k=oatmeal+bath"},
      {"name": "Antihistamines", "link": "https://www.1mg.com/categories/fitness-supplements/antihistamines-183"}
  ],
  "Dermato Fibroma": [
      {"name": "Moisturizing Lotion", "link": "https://www.amazon.in/s?k=moisturizing+lotion"},
      {"name": "Vitamin E Cream", "link": "https://www.amazon.in/s?k=vitamin+e+cream"},
      {"name": "Scar Gel", "link": "https://www.amazon.in/s?k=scar+removal+gel"}
  ],
  "Dyshidrotic Eczema": [
      {"name": "Hydrocortisone Cream", "link": "https://www.1mg.com/otc/hydrocortisone-cream-otc"},
      {"name": "Hand Moisturizer", "link": "https://www.amazon.in/s?k=hand+cream+for+dry+cracked+hands"},
      {"name": "Cotton Gloves", "link": "https://www.amazon.in/s?k=cotton+gloves"}
  ],
  "Melanoma": [
      {"name": "Broad-Spectrum Sunscreen", "link": "https://www.amazon.in/s?k=broad+spectrum+sunscreen"},
      {"name": "Protective Hat", "link": "https://www.amazon.in/s?k=sun+hat"},
      {"name": "Vitamin D3", "link": "https://www.1mg.com/search/all?name=Vitamin%20D3"}
  ],
  "Nail Fungus": [
      {"name": "Antifungal Nail Lacquer", "link": "https://www.amazon.in/s?k=antifungal+nail+paint"},
      {"name": "Tea Tree Oil", "link": "https://www.amazon.in/s?k=tea+tree+oil"},
      {"name": "Clotrimazole Cream", "link": "https://www.1mg.com/otc/clotrimazole-cream-otc"}
  ],
  "Nevus": [
      {"name": "Sunscreen SPF 50+", "link": "https://www.amazon.in/s?k=sunscreen+spf+50"},
      {"name": "Scar Gel", "link": "https://www.amazon.in/s?k=scar+gel"},
      {"name": "Vitamin E Oil", "link": "https://www.amazon.in/s?k=vitamin+e+oil"}
  ],
  "Normal Skin": [
      {"name": "Daily Moisturizer", "link": "https://www.amazon.in/s?k=daily+face+moisturizer"},
      {"name": "Gentle Cleanser", "link": "https://www.amazon.in/s?k=gentle+face+cleanser"},
      {"name": "Sunscreen SPF 30", "link": "https://www.amazon.in/s?k=sunscreen+spf+30"}
  ],
  "Pigmented Benign Keratosis": [
      {"name": "Moisturizer", "link": "https://www.amazon.in/s?k=moisturizing+cream"},
      {"name": "Vitamin E", "link": "https://www.1mg.com/search/all?name=Vitamin%20E"},
      {"name": "Sunscreen", "link": "https://www.amazon.in/s?k=sunscreen"}
  ],
  "Ringworm": [
      {"name": "Clotrimazole Cream", "link": "https://www.1mg.com/otc/clotrimazole-cream-otc"},
      {"name": "Ketoconazole Soap", "link": "https://www.amazon.in/s?k=ketoconazole+soap"},
      {"name": "Antifungal Powder", "link": "https://www.amazon.in/s?k=antifungal+powder"}
  ],
  "Seborrheic Keratosis": [
      {"name": "Moisturizing Lotion", "link": "https://www.amazon.in/s?k=moisturizer"},
      {"name": "Aloe Vera", "link": "https://www.amazon.in/s?k=aloe+vera+gel"},
      {"name": "Vitamin E", "link": "https://www.amazon.in/s?k=vitamin+e"}
  ],
  "Squamous Cell Carcinoma": [
      {"name": "SPF 50+ Sunscreen", "link": "https://www.amazon.in/s?k=spf+50+sunscreen"},
      {"name": "Protective Hat", "link": "https://www.amazon.in/s?k=uv+protection+hat"},
      {"name": "Aloe Vera", "link": "https://www.amazon.in/s?k=aloe+vera+gel"}
  ],
  "Vascular Lesion": [
      {"name": "Compression Stockings", "link": "https://www.amazon.in/s?k=compression+stockings"},
      {"name": "Vitamin C", "link": "https://www.1mg.com/search/all?name=Vitamin%20C"},
      {"name": "Moisturizer", "link": "https://www.amazon.in/s?k=body+moisturizer"}
  ],
  "Rosacea": [
      {"name": "Gentle Cleanser", "link": "https://www.amazon.in/s?k=gentle+cleanser+rosacea"},
      {"name": "Redness Relief Cream", "link": "https://www.amazon.in/s?k=redness+relief+cream"},
      {"name": "Sunscreen", "link": "https://www.amazon.in/s?k=mineral+sunscreen"}
  ],
  "Vitiligo": [
      {"name": "Sunscreen", "link": "https://www.amazon.in/s?k=sunscreen"},
      {"name": "Skin Camouflage Cream", "link": "https://www.amazon.in/s?k=skin+camouflage+cream"},
      {"name": "Vitamin D", "link": "https://www.1mg.com/search/all?name=Vitamin%20D"}
  ],
  "Impetigo": [
      {"name": "Antibiotic Ointment", "link": "https://www.1mg.com/search/all?name=antibiotic%20ointment"},
      {"name": "Antibacterial Soap", "link": "https://www.amazon.in/s?k=antibacterial+soap"},
      {"name": "Bandages", "link": "https://www.amazon.in/s?k=bandages"}
  ],
  "Scabies": [
      {"name": "Permethrin Cream", "link": "https://www.1mg.com/search/all?name=Permethrin"},
      {"name": "Soothing Lotion", "link": "https://www.amazon.in/s?k=calamine+lotion"},
      {"name": "Antihistamines", "link": "https://www.1mg.com/search/all?name=antihistamine"}
  ],
  "Shingles": [
      {"name": "Calamine Lotion", "link": "https://www.amazon.in/s?k=calamine+lotion"},
      {"name": "Cool Compress", "link": "https://www.amazon.in/s?k=cool+compress"},
      {"name": "Pain Relief Gel", "link": "https://www.amazon.in/s?k=pain+relief+gel"}
  ],
  "Psoriasis": [
      {"name": "Salicylic Acid Cream", "link": "https://www.amazon.in/s?k=salicylic+acid+cream"},
      {"name": "Coal Tar Shampoo", "link": "https://www.amazon.in/s?k=coal+tar+shampoo"},
      {"name": "Heavy Moisturizer", "link": "https://www.amazon.in/s?k=moisturizer+for+psoriasis"}
  ],
  "Eczema": [
      {"name": "Ceramide Cream", "link": "https://www.amazon.in/s?k=ceramide+cream"},
      {"name": "Hydrocortisone", "link": "https://www.1mg.com/search/all?name=hydrocortisone"},
      {"name": "Oatmeal Bath", "link": "https://www.amazon.in/s?k=oatmeal+bath"}
  ]
}

DISEASE_DESCRIPTIONS = {
    "Acne": "Acne is a skin condition that occurs when your hair follicles become plugged with oil and dead skin cells.",
    "Actinic Keratosis": "A rough, scaly patch on the skin caused by years of sun exposure. It is a precancerous lesion.",
    "Basal Cell Carcinoma": "A type of skin cancer that begins in the basal cells.",
    "Chickenpox": "A highly contagious viral infection causing an itchy, blister-like rash on the skin.",
    "Dermato Fibroma": "A common overgrowth of fibrous tissue situated in the dermis.",
    "Dyshidrotic Eczema": "A condition in which small, itchy blisters develop on the edges of the fingers, toes, palms, and soles.",
    "Melanoma": "The most serious type of skin cancer. Melanoma occurs when pigment-producing cells become cancerous.",
    "Nail Fungus": "A common condition that begins as a white or yellow spot under the tip of your fingernail or toenail.",
    "Nevus": "A common pigmented skin lesion, usually developing during adulthood. Also known as a mole.",
    "Normal Skin": "Healthy skin with no visible signs of dermatological disease.",
    "Pigmented Benign Keratosis": "A common, non-cancerous skin growth. People tend to get more of them as they get older.",
    "Ringworm": "A contagious fungal infection characterized by a circular, raised, scaly rash that may be itchy.",
    "Seborrheic Keratosis": "A non-cancerous skin condition that appears as a waxy brown, black, or tan growth.",
    "Squamous Cell Carcinoma": "A common form of skin cancer that develops in the squamous cells of the middle and outer layers of skin.",
    "Vascular Lesion": "Abnormalities of the skin and underlying tissues involving the blood vessels.",
    "Rosacea": "A common skin condition that causes blushing or flushing and visible blood vessels in your face.",
    "Vitiligo": "A disease that causes the loss of skin color in blotches due to lack of melanin.",
    "Impetigo": "A common and highly contagious skin infection that mainly affects infants and young children.",
    "Scabies": "An itchy skin condition caused by a tiny burrowing mite called Sarcoptes scabiei.",
    "Shingles": "A viral infection that causes a painful rash, caused by the varicella-zoster virus.",
    "Psoriasis": "A skin disease that causes a rash with itchy, scaly patches, most commonly on the knees and elbows.",
    "Eczema": "A condition that makes your skin red and itchy. It's common in children but can occur at any age."
}

DISEASE_SYMPTOMS = {
    "Acne": ["Whiteheads", "Blackheads", "Small red bumps (papules)", "Pimples (pustules)", "Painful lumps under the skin"],
    "Actinic Keratosis": ["Rough, dry, or scaly patch of skin", "Flat to slightly raised bump", "Hard, wart-like surface", "Itching or burning in the affected area"],
    "Basal Cell Carcinoma": ["A pearly or waxy bump", "A flat, flesh-colored or brown scar-like lesion", "A bleeding or scabbing sore that heals and returns"],
    "Chickenpox": ["Itchy, red fluid-filled blisters", "Fever", "Loss of appetite", "Headache and fatigue"],
    "Dermato Fibroma": ["Small, firm, brownish-red growth", "Usually found on the legs", "Tender or itchy when touched", "Dimples inward when pinched"],
    "Dyshidrotic Eczema": ["Tiny, fluid-filled blisters (vesicles)", "Deep-seated itching on palms or soles", "Redness and sweating around blisters", "Cracked or peeling skin after blisters dry"],
    "Melanoma": ["Large brownish spot with darker speckles", "Mole that changes in color or size", "Small lesion with an irregular border", "Dark lesions on palms, soles, or fingertips"],
    "Nail Fungus": ["Thickened nails", "Whitish to yellow-brown discoloration", "Brittle, crumbly, or ragged edges", "Distorted nail shape", "Dark color caused by debris building up under the nail"],
    "Nevus": ["Uniform tan, brown, or black spot", "Distinct borders", "Usually round or oval", "Flat or slightly raised surface"],
    "Normal Skin": ["No visible lesions", "Consistent skin tone", "Smooth texture", "Absence of inflammation or irritation"],
    "Pigmented Benign Keratosis": ["Flat, dark-colored patch", "Waxy or scaly appearance", "Well-defined edges", "Often mistaken for a mole or freckle"],
    "Ringworm": ["Ring-shaped rash", "Clearer center inside the ring", "Red, scaly, or itchy skin", "Slightly raised expanding rings"],
    "Seborrheic Keratosis": ["Waxy, 'stuck-on' look", "Range in color from light tan to black", "Round or oval shape", "Often itchy and may look like a wart"],
    "Squamous Cell Carcinoma": ["Firm, red nodule", "Flat sore with a scaly crust", "New sore or raised area on an old scar or ulcer", "Rough, scaly patch on the lip"],
    "Vascular Lesion": ["Red, purple, or blue skin discoloration", "Visible blood vessels (telangiectasia)", "Birthmarks (like port-wine stains)", "Small red dots (cherry angiomas)"],
    "Rosacea": ["Facial redness and flushing", "Visible blood vessels", "Swollen red bumps", "Eye irritation (Ocular Rosacea)", "Enlarged nose (Rhinophyma)"],
    "Vitiligo": ["Patchy loss of skin color", "Premature whitening or graying of hair", "Loss of color in the tissues inside the mouth (mucous membranes)"],
    "Impetigo": ["Red sores that quickly rupture", "Ooze for a few days and then form a yellowish-brown crust", "Itching and soreness", "Fluid-filled blisters"],
    "Scabies": ["Severe itching, especially at night", "Thin, irregular burrow tracks made of tiny blisters", "Bumps on skin folds (webbing between fingers, armpits, waist)"],
    "Shingles": ["Pain, burning, or tingling sensation", "Sensitivity to touch", "Red rash that begins a few days after the pain", "Fluid-filled blisters that break open and crust over"],
    "Psoriasis": ["Red patches of skin covered with thick, silvery scales", "Small scaling spots", "Dry, cracked skin that may bleed", "Itching, burning, or soreness"],
    "Eczema": ["Dry, itchy skin", "Red to brownish-gray patches", "Small, raised bumps that may leak fluid", "Thickened, cracked, or scaly skin"],
}

# ---------------------------------------------------------
# MODEL LOADING
# ---------------------------------------------------------
MODEL_BASE_PATH = r"C:\Users\aksha\Downloads\skinsense\skinsense\dataset"

try:
    loaded = joblib.load(os.path.join(MODEL_BASE_PATH, r"C:\Users\aksha\Downloads\skinsense\skinsense\dataset\skin_disease_model.pkl"))
    if isinstance(loaded, tuple):
        disease_model, classes = loaded 
    else:
        disease_model = loaded
        classes = None
except Exception as e:
    print(f"Error loading Joblib model: {e}")
    disease_model = None
    classes = None

# ✅ REMOVED: Old CNN model loading (tf.keras)
# cnn_model = None  # No longer needed
CNN_MODEL_PATH = r"C:\Users\aksha\Downloads\skinsense\skinsense\dataset\skin_disease_model.h5"

try:
    cnn_model = tf.keras.models.load_model(CNN_MODEL_PATH)
    print("✅ H5 Model Loaded Successfully")
except Exception as e:
    print(f"❌ Error loading H5 model: {e}")
    cnn_model = None
def predict_skin_disease_image(image_path):
    if cnn_model is None:
        return "Model not loaded", 0.0

    try:
        # ⚠️ IMPORTANT: Match training size
        img = image.load_img(image_path, target_size=(224, 224))  
        img_array = image.img_to_array(img)

        # Normalize
        img_array = img_array / 255.0

        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)

        # Predict
        preds = cnn_model.predict(img_array)

        predicted_index = np.argmax(preds)
        confidence = float(np.max(preds) * 100)

        # Map class
        predicted_class = class_names[predicted_index]

        print("Prediction:", predicted_class)
        print("Confidence:", confidence)

        return predicted_class, confidence

    except Exception as e:
        print("Prediction Error:", e)
        return "Error", 0.0

# ✅ NEW: Load YOLO model from the provided path
YOLO_MODEL_PATH =r"C:\Users\aksha\Downloads\skinsense\skinsense\dataset\zipped_folder1 (2)\detect\train\weights\best.pt"
try:
    yolo_model = YOLO(YOLO_MODEL_PATH)
except Exception as e:
    print(f"Error loading YOLO model: {e}")
    yolo_model = None

# ✅ UPDATED: Class names (ensure they match your YOLO model's trained classes)
# Assuming your YOLO model uses the same classes; adjust if needed based on your labels
class_names = [
    'Acne', 'Actinic Keratosis', 'Basal Cell Carcinoma', 'Chickenpox',
    'Dermato Fibroma', 'Dyshidrotic Eczema', 'Melanoma', 'Nail Fungus',
    'Nevus', 'Normal Skin', 'Pigmented Benign Keratosis', 'Ringworm',
    'Seborrheic Keratosis', 'Squamous Cell Carcinoma', 'Vascular Lesion'
]

genai.configure(api_key="AIzaSyD1KWXLn3jdFGX9Y2m7RODUPiZupTamIbc")
ai_model = genai.GenerativeModel("gemini-2.0-flash")

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

# ✅ UPDATED: predict_skin_disease_image to use YOLO instead of CNN
def predict_skin_disease_image(image_path):
    if yolo_model is None:
        return "Model not loaded", 0.0

    # Run YOLO inference on the image
    results = yolo_model(image_path)

    # Process results: Assuming single main detection; get the class with highest confidence
    # If multiple detections, you can aggregate or select the top one
    if results and len(results) > 0:
        top_result = results[0]  # First result (for single image)
        if top_result.boxes:  # If detections exist
            # Get the index of the class with highest confidence
            confs = top_result.boxes.conf.cpu().numpy()  # Confidences
            classes_idx = top_result.boxes.cls.cpu().numpy()  # Class indices
            max_conf_idx = np.argmax(confs)
            predicted_index = int(classes_idx[max_conf_idx])
            confidence = float(confs[max_conf_idx] * 100)

            # Map to class name (ensure class_names matches YOLO's class order)
            predicted_class = class_names[predicted_index] if predicted_index < len(class_names) else "Unknown"
            return predicted_class, confidence

    # Fallback if no detections
    return "No detection", 0.0

# ---------------------------------------------------------
# VIEWS
# ---------------------------------------------------------

def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == "POST":
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        username = request.POST.get('username')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        if password != cpassword:
            messages.error(request, "Passwords do not match!")
            return redirect("register")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("register")
        user = User.objects.create_user(username=username, password=password)
        user.first_name = fname
        user.last_name = lname
        user.save()
        messages.success(request, "Your Account has been Created.")
        return redirect("log_in")
    return render(request, "register.html")

def log_in(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if not Doctor.objects.filter(user=user).exists():
                login(request, user)
                messages.success(request, "Log In Successful!")
                return redirect("index")
            else:
                messages.error(request, "Doctors cannot login here.")
                return redirect("log_in")
        else:
            messages.error(request, "Invalid Username or Password.")
            return redirect("log_in")
    return render(request, "log_in.html", {'action': 'log_in'})

def log_out(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("/")


def dashboard(request):
    # Pre-fetch records to avoid repeating code
    my_records = PatientSkinData.objects.filter(user=request.user).order_by('-id')
    latest_record = my_records.first() if my_records.exists() else None

    if request.method == "POST":
        form = skin_symptom_form(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            patient = PatientSkinData.objects.create(
                user=request.user,
                first_name=data["first_name"],
                last_name=data["last_name"],
                age=data["age"],
                contact=data["contact"],
                sym1=data["sym1"], sym2=data["sym2"], sym3=data["sym3"],
                sym4=data["sym4"], sym5=data["sym5"], sym6=data["sym6"],
                sym7=data["sym7"], sym8=data["sym8"], sym9=data["sym9"],
                sym10=data["sym10"],
            )

            # --- Prediction Logic ---
            selected_syms = [data[f"sym{i}"] for i in range(1, 11) if data[f"sym{i}"] not in [None, "", "default"]]
            vector = [0] * 20
            for s in selected_syms:
                if s.isdigit() and int(s) < 20:
                    vector[int(s)] = 1

            if disease_model:
                prediction_index = disease_model.predict([vector])[0]
                prediction = classes[prediction_index] if classes and isinstance(prediction_index, (int, np.integer)) else str(prediction_index)
            else:
                prediction = "Unknown"

            patient.predicted_disease = prediction
            patient.save()
            
            # --- Fetching Result Data ---
            doctor_info = next((d["doctors"] for d in DOCTORS_DATA if d["disease"] == prediction), [])
            precautions_info = next((p["precautions"] for p in PRECAUTIONS_DATA if p["disease"] == prediction), [])
            products_info = PRODUCTS_DATA.get(prediction, [])
            description_info = DISEASE_DESCRIPTIONS.get(prediction, "No description available.")
            
            reported_symptoms = []
            for i in range(1, 11):
                val = getattr(patient, f"sym{i}")
                if val and val != "default":
                    reported_symptoms.append(SYMPTOM_INDEX_MAP.get(str(val), val) if str(val).isdigit() else val)

            messages.success(request, f"Predicted Disease: {prediction}")
            return render(request, "NonMRI_Predict.html", {
                "patient": patient,
                "doctors": doctor_info,
                "precautions": precautions_info,
                "products": products_info,
                "description": description_info,
                "reported_symptoms": reported_symptoms
            })
    else:
        form = skin_symptom_form()

    return render(request, "dashboard.html", {
        "form": form, 
        "my_records": my_records, 
        "latest_record": latest_record
    })
@login_required
def mri(request):
    if request.method == "POST":
        # 1. Get Data from Form
        fname = request.POST.get("patient_fname")
        lname = request.POST.get("patient_lname")
        age = request.POST.get("patient_age")
        mobile = request.POST.get("patient_mob_no")
        
        patient_data = {
            "fname": fname, "lname": lname, "age": age, "mobile": mobile,
        }
        
        prediction, confidence = None, None
        img_path_for_session = None
        
        # Variable to hold file for database saving
        image_file_to_save = None

        try:
            # 2. Handle Image & Prediction
            if "image" in request.FILES:
                file = request.FILES["image"]
                image_file_to_save = file

                file_name = default_storage.save(file.name, file)
                file_path = default_storage.path(file_name)
                prediction, confidence = predict_skin_disease_image(file_path)
                img_path_for_session = file_path 

            elif "image_data" in request.POST:
                image_data = request.POST["image_data"]
                if image_data.startswith("data:image"):
                    format, imgstr = image_data.split(";base64,")
                    ext = format.split("/")[-1]
                    
                    # Create ContentFile
                    image_file_to_save = ContentFile(base64.b64decode(imgstr), name=f"cam_{datetime.datetime.now().timestamp()}.{ext}")

                    file_name = default_storage.save(image_file_to_save.name, image_file_to_save)
                    file_path = default_storage.path(file_name)
                    
                    prediction, confidence = predict_skin_disease_image(file_path)
                    img_path_for_session = file_path 

            if prediction:
                # --- NEW LOGIC: SAVE TO DATABASE (WITH USER LINK) ---
                new_patient = MRIPatientData(
                    user=request.user,  # ✅ ADDED: This connects the scan to your history
                    fname=fname,
                    lname=lname,
                    age=age,
                    mobile=mobile,
                    predicted_disease=prediction,
                    # ✅ Save Confidence
                    confidence=float(confidence) if confidence else 0.0,
                    status="Pending"
                )
                
                # ✅ Save Image to Database Field
                if image_file_to_save:
                    # Reset file pointer so it saves correctly
                    if hasattr(image_file_to_save, 'seek'):
                        image_file_to_save.seek(0)
                    new_patient.image.save(image_file_to_save.name, image_file_to_save, save=False)
                
                new_patient.save()
                
                # Save ID to session
                request.session["mri_patient_id"] = new_patient.id 
                
                # Keep existing session data for display
                request.session["patient_data"] = patient_data
                request.session["prediction"] = prediction
                request.session["confidence"] = f"{confidence:.2f}"
                request.session["image_path"] = img_path_for_session 

                return redirect("MRI_Predict")

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    # ✅ UPDATED: Fetch the last patient belonging ONLY to the logged-in user
    last_patient = MRIPatientData.objects.filter(user=request.user).last()
    return render(request, "mri.html", {"last_patient": last_patient})

def MRI_Predict(request):
    patient_data = request.session.get("patient_data", {})
    prediction = request.session.get("prediction", None)
    confidence = request.session.get("confidence", None)
    doctor_suggestion = None
    patient_id = request.session.get("mri_patient_id")
    precautions = []
    products = []
    if prediction:
        doctors_entry = next((d for d in DOCTORS_DATA if d["disease"].lower() == prediction.lower()), None)
        if doctors_entry:
            doctor_suggestion = random.choice(doctors_entry["doctors"])
        
        precautions_entry = next((p for p in PRECAUTIONS_DATA if p["disease"].lower() == prediction.lower()), None)
        if precautions_entry:
            precautions = precautions_entry["precautions"]
            
        products = PRODUCTS_DATA.get(prediction, [])
        
        request.session["doctor_suggestion"] = doctor_suggestion
        request.session["precautions"] = precautions
        request.session["products"] = products 
    return render(request, "MRI_Predict.html", {
        "patient": patient_data,
        "prediction": prediction,
        "confidence": confidence,
        "doctor": doctor_suggestion,
        "precautions": precautions,
        "products": products,
        "patient_id": patient_id,
    })

def NonMRI_Predict(request):
    return render(request, 'NonMRI_Predict.html')

def mid(request):
    return render(request, "mid.html")

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def faq(request):
    return render(request, 'faq.html')

# app/views.py

@login_required
def book_appointment(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient_id")
        doctor_email = request.POST.get("doctor_email").strip()
        patient = get_object_or_404(PatientSkinData, id=patient_id)
        try:
            doctor = Doctor.objects.get(user__username__iexact=doctor_email)
        except Doctor.DoesNotExist:
            messages.error(request, "Doctor not registered.")
            return redirect("NonMRI_Predict")
        patient.doctor = doctor
        patient.save()
        messages.success(request, f"Appointment booked with Dr. {doctor.user.first_name}")
        return redirect("appointment_result", patient_id=patient.id)
    return redirect("NonMRI_Predict")

@login_required
def appointment_result(request, patient_id):
    patient = get_object_or_404(PatientSkinData, id=patient_id)
    prediction = patient.predicted_disease
    
    # Re-fetch context so appointment result page isn't empty
    precautions_info = next((p["precautions"] for p in PRECAUTIONS_DATA if p["disease"] == prediction), [])
    products_info = PRODUCTS_DATA.get(prediction, [])
    description_info = DISEASE_DESCRIPTIONS.get(prediction, "")
    
    reported_symptoms = []
    for i in range(1, 11):
        val = getattr(patient, f"sym{i}")
        if val and val != "default":
            if str(val).isdigit():
                reported_symptoms.append(SYMPTOM_INDEX_MAP.get(str(val), val))
            else:
                reported_symptoms.append(val)

    return render(request, "appointment_result.html", {
        "patient": patient, 
        "precautions": precautions_info,
        "products": products_info,
        "description": description_info,
        "reported_symptoms": reported_symptoms
    })

# --- CORRECTED MRI FUNCTIONS START HERE ---

@login_required
def book_mri_appointment(request):
    if request.method == "POST":
        # 1. Get Patient ID from hidden input (Linking to the scan we just did)
        patient_id = request.POST.get("patient_id")
        doctor_email = request.POST.get("doctor_email").strip()

        if not patient_id:
            messages.error(request, "Error: Patient record not found. Please rescan.")
            return redirect("MRI_Predict")

        # 2. Fetch the EXISTING record
        patient = get_object_or_404(MRIPatientData, id=patient_id)

        try:
            doctor = Doctor.objects.get(user__username__iexact=doctor_email)
        except Doctor.DoesNotExist:
            messages.error(request, "Doctor not registered.")
            return redirect("MRI_Predict")

        # 3. Update the existing record with the Doctor
        patient.doctor = doctor
        patient.status = "Pending"
        patient.save()

        messages.success(request, f"Appointment booked with Dr. {doctor.user.first_name}")
        return redirect("mri_appointment_result", patient_id=patient.id)
    
    return redirect("MRI_Predict")

@login_required
def mri_appointment_result(request, patient_id):
    """
    Displays the appointment confirmation for MRI Patients.
    Re-uses the 'appointment_result.html' template but enables MRI-specific features.
    """
    # 1. Fetch the MRI Patient Record
    patient = get_object_or_404(MRIPatientData, id=patient_id)
    prediction = patient.predicted_disease
    
    # 2. Fetch Context Data
    precautions_info = next((p["precautions"] for p in PRECAUTIONS_DATA if p["disease"].lower() == prediction.lower()), [])
    products_info = PRODUCTS_DATA.get(prediction, [])
    description_info = DISEASE_DESCRIPTIONS.get(prediction, "No description available.")

    # 3. Render the SHARED template with MRI Flags
    return render(request, "appointment_result_mri.html", {
        "patient": patient, 
        "precautions": precautions_info,
        "products": products_info,
        "description": description_info,
        
        # ✅ MRI-Specific Context Flags
        "is_mri": True,               
        "confidence": patient.confidence, 
        "reported_symptoms": [] 
    })

# --- NON-MRI PDF GENERATION (ReportLab) ---
@login_required
def download_pdf(request, patient_id):
    """
    Non-MRI Report Generator with Namespace Fix.
    Includes: Patient Info, Condition Details, Reported Symptoms, Care Tips, Products, and Doctors.
    """
    # ✅ FIX: Import settings as 'conf' to avoid naming conflict with your 'settings' view
    from django.conf import settings as conf
    import os

    # --- 1. DATA RETRIEVAL ---
    patient = get_object_or_404(PatientSkinData, id=patient_id)
    prediction = patient.predicted_disease
    
    # Fetch content from your constants
    precautions = next((p["precautions"] for p in PRECAUTIONS_DATA if p["disease"] == prediction), [])
    products = PRODUCTS_DATA.get(prediction, [])
    description = DISEASE_DESCRIPTIONS.get(prediction, "No description available.")
    
    doctor_suggestion = None
    doctors_entry = next((d for d in DOCTORS_DATA if d["disease"].lower() == prediction.lower()), None)
    if doctors_entry and doctors_entry.get("doctors"):
        doctor_suggestion = doctors_entry["doctors"][0]

    fname = patient.first_name
    lname = patient.last_name
    full_name = f"{fname} {lname}"

    # --- 2. PDF SETUP ---
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="SkinSense_Report_{fname}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    
    skin_color = colors.HexColor('#dc9b7d')
    dark_text = colors.HexColor('#333333')
    styles = getSampleStyleSheet()
    
    style_brand = ParagraphStyle('Brand', fontName='Helvetica-Bold', fontSize=20, textColor=skin_color, spaceAfter=2)
    style_normal = ParagraphStyle('NormalText', fontName='Helvetica', fontSize=10, textColor=dark_text, leading=14, spaceAfter=6)
    style_disclaimer = ParagraphStyle('Disclaimer', fontName='Helvetica-Oblique', fontSize=8, textColor=colors.gray, alignment=TA_CENTER, spaceBefore=30)

    # ✅ FIXED LOGO PATH (Uses 'conf' instead of 'settings')
    logo_path = os.path.join(conf.BASE_DIR, 'static', 'assets', 'img', 'sa-1.ico')
    logo_flowable = []
    if os.path.exists(logo_path):
        try:
            img = ReportLabImage(logo_path, width=0.5*inch, height=0.5*inch)
            logo_flowable.append(img)
        except:
            pass

    header_data = [[
        logo_flowable, 
        Paragraph("SkinSense", style_brand),
        Paragraph(f"Ref: SYM-{patient.id}", ParagraphStyle('R', alignment=TA_RIGHT, fontName='Helvetica', fontSize=10, textColor=colors.gray))
    ]]
    
    header_table = Table(header_data, colWidths=[0.5*inch, 2*inch, 4.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
        ('LEFTPADDING', (0,0), (0,0), 0),
        ('RIGHTPADDING', (0,0), (0,0), 0),    
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))
    elements.append(Table([[""]], colWidths=[7*inch], style=[('LINEBELOW', (0,0), (-1,-1), 1, skin_color)]))
    elements.append(Spacer(1, 15))

    # --- 3. PATIENT INFORMATION ---
    info_text = [
        Paragraph(f"<b>Report Date:</b> {datetime.date.today().strftime('%B %d, %Y')}", style_normal),
        Paragraph(f"<b>Patient Name:</b> {full_name}", style_normal),
        Paragraph(f"<b>Age:</b> {patient.age}", style_normal),
        Paragraph(f"<b>Contact:</b> {patient.contact}", style_normal),
        Spacer(1, 10),
        Paragraph(f"<b>AI Analysis Result:</b>", style_normal),
        Paragraph(f"<font size=14 color='#dc9b7d'><b>{prediction}</b></font>", style_normal),
    ]
    info_table = Table([[info_text]], colWidths=[7*inch])
    info_table.setStyle(TableStyle([('LEFTPADDING', (0,0), (0,0), 0)]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))

    def create_section_header(text):
        return Table([[Paragraph(text, ParagraphStyle('S', fontName='Helvetica-Bold', fontSize=11, textColor=colors.white))]], 
                      colWidths=[7*inch], 
                      style=[('BACKGROUND', (0,0), (-1,-1), skin_color), ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)])

    # Condition Details
    elements.append(create_section_header("Condition Overview"))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(description, style_normal))
    elements.append(Spacer(1, 10))

    # Symptoms Section
    elements.append(create_section_header("Analysis of Reported Symptoms"))
    elements.append(Spacer(1, 5))
    patient_symptoms = []
    for i in range(1, 11):
        val = getattr(patient, f"sym{i}")
        if val and val != "default" and val != "":
             if str(val).isdigit():
                 patient_symptoms.append(SYMPTOM_INDEX_MAP.get(str(val), val))
             else:
                 patient_symptoms.append(str(val))
    
    if patient_symptoms:
        for sym in patient_symptoms:
             elements.append(Paragraph(f"• {sym}", style_normal))
    else:
        elements.append(Paragraph("No specific symptoms were highlighted in this session.", style_normal))
    elements.append(Spacer(1, 10))

    # Care Tips
    if precautions:
        elements.append(create_section_header(" Precautions"))
        elements.append(Spacer(1, 5))
        for p in precautions:
            elements.append(Paragraph(f"• {p}", style_normal))
        elements.append(Spacer(1, 10))

    # Products
    if products:
        elements.append(create_section_header("Product Recommendations"))
        elements.append(Spacer(1, 5))
        for prod in products:
            p_name = prod['name'] if isinstance(prod, dict) else prod
            elements.append(Paragraph(f"• {p_name}", style_normal))
        elements.append(Spacer(1, 10))

    # Suggested Doctor
    if doctor_suggestion:
        elements.append(create_section_header("Suggested Specialist"))
        elements.append(Spacer(1, 5))
        doc_text = f"<b>{doctor_suggestion['name']}</b><br/>{doctor_suggestion['specialization']}<br/>{doctor_suggestion['location']}<br/>Contact: {doctor_suggestion.get('email', 'N/A')}"
        elements.append(Paragraph(doc_text, style_normal))
        elements.append(Spacer(1, 10))

    # Assigned Doctor (if applicable)
    if patient.doctor:
        elements.append(create_section_header("Assigned Doctor"))
        elements.append(Spacer(1, 5))
        doc_info = f"Dr. {patient.doctor.user.first_name} {patient.doctor.user.last_name} ({patient.doctor.specialization})"
        elements.append(Paragraph(doc_info, style_normal))
        elements.append(Spacer(1, 10))

    # Footer Disclaimer
    elements.append(Spacer(1, 30))
    elements.append(Table([[""]], colWidths=[7*inch], style=[('LINEBELOW', (0,0), (-1,-1), 0.5, colors.lightgrey)]))
    elements.append(Spacer(1, 5))
    
    disclaimer_text = """
    <b>Medical Disclaimer:</b> This report is generated by the SkinSense AI Symptom Analyzer for informational purposes. 
    It is <b>not</b> a substitute for clinical diagnosis. 
    Please consult with a medical professional immediately if your symptoms persist or worsen.
    <br/><br/>
    &copy; 2026 SkinSense. All rights reserved.
    """
    elements.append(Paragraph(disclaimer_text, style_disclaimer))

    # --- 4. BUILD PDF ---
    doc.build(elements)
    return response


@login_required
def download_pdf_mri(request, patient_id=None):
    """
    MRI Report Generator with Namespace Fix.
    - If patient_id is provided -> Fetches from Database (Doctor/History View).
    - If no patient_id -> Fetches from Session (Immediate Patient View).
    """
  # --- 1. DATA RETRIEVAL ---
    fname, lname, prediction, confidence = "Unknown", "", "Unknown", "0"
    precautions, products, image_path = [], [], None
    doctor_suggestion = None
    patient = None  # ✅ Initialize patient as None

    if patient_id:
        patient = get_object_or_404(MRIPatientData, id=patient_id)
        fname = patient.fname
        lname = patient.lname
        prediction = patient.predicted_disease
        confidence = str(patient.confidence) if patient.confidence else "0"
        if patient.image:
            try:
                image_path = patient.image.path
            except:
                image_path = None
        
        # Static data re-fetch
        prec_entry = next((p for p in PRECAUTIONS_DATA if p["disease"].lower() == prediction.lower()), None)
        if prec_entry: precautions = prec_entry["precautions"]
        products = PRODUCTS_DATA.get(prediction, [])
        
        if patient.doctor:
            doctor_suggestion = {
                "name": f"Dr. {patient.doctor.user.first_name} {patient.doctor.user.last_name}",
                "specialization": patient.doctor.specialization,
                "location": patient.doctor.location,
                "email": patient.doctor.user.email
            }
    else:
        patient_data = request.session.get("patient_data", {})
        fname = patient_data.get("fname", "Unknown")
        lname = patient_data.get("lname", "")
        prediction = request.session.get("prediction", "Unknown")
        confidence = request.session.get("confidence", "0")
        precautions = request.session.get("precautions", [])
        products = request.session.get("products", [])
        doctor_suggestion = request.session.get("doctor_suggestion", None)
        image_path = request.session.get("image_path", None)

    full_name = f"{fname} {lname}"

    # --- 2. PDF GENERATION ---
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SkinSense_Report_{fname}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []

    skin_color = colors.HexColor('#dc9b7d')
    dark_text = colors.HexColor('#333333')
    styles = getSampleStyleSheet()
    
    style_brand = ParagraphStyle('Brand', fontName='Helvetica-Bold', fontSize=20, textColor=skin_color, spaceAfter=2)
    style_normal = ParagraphStyle('NormalText', fontName='Helvetica', fontSize=10, textColor=dark_text, leading=14, spaceAfter=6)
    style_disclaimer = ParagraphStyle('Disclaimer', fontName='Helvetica-Oblique', fontSize=8, textColor=colors.gray, alignment=TA_CENTER, spaceBefore=30)

    logo_path = os.path.join(conf.BASE_DIR, 'static', 'assets', 'img', 'sa-1.ico')
    logo_flowable = []
    if os.path.exists(logo_path):
        try:
            img = ReportLabImage(logo_path, width=0.5*inch, height=0.5*inch)
            logo_flowable.append(img)
        except: pass

    header_data = [[
        logo_flowable, 
        Paragraph("SkinSense", style_brand),
        Paragraph(f"Ref ID: {patient_id if patient_id else 'TMP-'+str(random.randint(1000,9999))}", 
                  ParagraphStyle('R', alignment=TA_RIGHT, fontSize=10, textColor=colors.gray))
    ]]
    
    header_table = Table(header_data, colWidths=[0.5*inch, 3*inch, 3.5*inch])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (2,0), (2,0), 'RIGHT')]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))
    elements.append(Table([[""]], colWidths=[7*inch], style=[('LINEBELOW', (0,0), (-1,-1), 1, skin_color)]))
    elements.append(Spacer(1, 15))

    # Info & Image
    img_flowable = []
    if image_path and os.path.exists(image_path):
        try:
            im = ReportLabImage(image_path, width=2.2*inch, height=2.2*inch)
            im.hAlign = 'CENTER'
            img_flowable.append(im)
            img_flowable.append(Paragraph("Analysis Visualization", ParagraphStyle('C', alignment=TA_CENTER, fontSize=8, textColor=colors.gray)))
        except: img_flowable.append(Paragraph("[Image Process Error]", style_normal))
    else: img_flowable.append(Paragraph("[No Scan Image]", style_normal))

    info_text = [
        Paragraph(f"<b>Report Date:</b> {datetime.date.today().strftime('%B %d, %Y')}", style_normal),
        Paragraph(f"<b>Patient Name:</b> {full_name}", style_normal),
        Paragraph(f"<b>Analysis Type:</b> MRI/Visual AI Scan", style_normal),
        Spacer(1, 10),
        Paragraph(f"<b>Potential Condition:</b>", style_normal),
        Paragraph(f"<font size=14 color='#dc9b7d'><b>{prediction}</b></font>", style_normal),
        Spacer(1, 5),
        Paragraph(f"<b>AI Confidence:</b> {confidence}%", style_normal),
    ]

    main_table = Table([[img_flowable, info_text]], colWidths=[2.8*inch, 4.2*inch])
    main_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (1,0), (1,0), 20)]))
    elements.append(main_table)
    elements.append(Spacer(1, 20))

    def create_section_header(text):
        return Table([[Paragraph(text, ParagraphStyle('S', fontName='Helvetica-Bold', fontSize=11, textColor=colors.white))]], 
                     colWidths=[7*inch], 
                     style=[('BACKGROUND', (0,0), (-1,-1), skin_color), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)])

    # Condition Details
    elements.append(create_section_header("AI Diagnostic Summary"))
    elements.append(Spacer(1, 5))
    description = DISEASE_DESCRIPTIONS.get(prediction, f"{prediction} is a dermatological condition identified via convolutional neural network analysis.")
    elements.append(Paragraph(description, style_normal))
    elements.append(Spacer(1, 10))

    # Symptoms
    elements.append(create_section_header(f" Symptoms  {prediction}"))
    elements.append(Spacer(1, 5))
    symptoms_list = DISEASE_SYMPTOMS.get(prediction, DISEASE_SYMPTOMS.get("default", ["Consult a doctor for symptom verification."]))
    for sym in symptoms_list:
        elements.append(Paragraph(f"• {sym}", style_normal))
    elements.append(Spacer(1, 10))

    # Care Tips
    if precautions:
        elements.append(create_section_header(" Precautions"))
        elements.append(Spacer(1, 5))
        for p in precautions:
            elements.append(Paragraph(f"• {p}", style_normal))
        elements.append(Spacer(1, 10))

    # Products
    if products:
        elements.append(create_section_header("Product Recommendations"))
        elements.append(Spacer(1, 5))
        for prod in products:
            p_name = prod['name'] if isinstance(prod, dict) else prod
            elements.append(Paragraph(f"• {p_name}", style_normal))
        elements.append(Spacer(1, 10))

    # Specialist (Static/Session suggestion)
    if doctor_suggestion:
        elements.append(create_section_header("Suggested Specialist"))
        elements.append(Spacer(1, 5))
        doc_text = f"<b>{doctor_suggestion['name']}</b><br/>{doctor_suggestion['specialization']}<br/>{doctor_suggestion['location']}"
        elements.append(Paragraph(doc_text, style_normal))
        elements.append(Spacer(1, 10))
    
    # ✅ FIX: Check if 'patient' exists before accessing 'patient.doctor'
    if patient and patient.doctor:
        elements.append(create_section_header("Assigned Doctor"))
        elements.append(Spacer(1, 5))
        doc_info = f"Dr. {patient.doctor.user.first_name} {patient.doctor.user.last_name} ({patient.doctor.specialization})"
        elements.append(Paragraph(doc_info, style_normal))
        elements.append(Spacer(1, 10))

    # Footer
    elements.append(Spacer(1, 30))
    elements.append(Table([[""]], colWidths=[7*inch], style=[('LINEBELOW', (0,0), (-1,-1), 0.5, colors.lightgrey)]))
    
    disclaimer_text = """
    <b>Medical Disclaimer:</b> This report is generated by the SkinSense AI Engine. 
    It is provided for screening purposes only and <b>does not constitute a medical diagnosis</b>. 
    Always verify AI findings with a licensed Dermatologist.
    """
    elements.append(Paragraph(disclaimer_text, style_disclaimer))

    # Build PDF
    doc.build(elements)
    return response

@csrf_exempt
def chatbot_api(request):
    if request.method != "POST":
        return JsonResponse({"reply": "Method not allowed."}, status=405)
        
    try:
        data = json.loads(request.body.decode("utf-8"))
        message = data.get("message", "").strip()
        
        if not message:
            return JsonResponse({"reply": "Please type a message."})
            
        message_lower = message.lower()
        all_diseases = list(set(list(DISEASE_DESCRIPTIONS.keys()) + list(DISEASE_SYMPTOMS.keys()) + list(PRODUCTS_DATA.keys())))

        # --- 1. KNOWLEDGE MATRIX INJECTION FOR LIVE GEMINI (PREFERS ACTIVE API KEY) ---
        knowledge_matrix = "SECURE PLATFORM CLINICAL REFERENCE DATA:\n"
        for disease in all_diseases:
            desc = DISEASE_DESCRIPTIONS.get(disease, "")
            symptoms_list = DISEASE_SYMPTOMS.get(disease, [])
            products = PRODUCTS_DATA.get(disease, [])
            doc_entry = next((d for d in DOCTORS_DATA if d["disease"].lower() == disease.lower()), None)
            doctors = doc_entry["doctors"] if doc_entry else []
            
            knowledge_matrix += f"\n[DISEASE: {disease}]\n"
            knowledge_matrix += f"- Overview: {desc}\n"
            if symptoms_list:
                knowledge_matrix += f"- Clinical Symptoms: {', '.join(symptoms_list)}\n"
            if products:
                knowledge_matrix += f"- Recommended Products: {', '.join([p['name'] for p in products])}\n"
            if doctors:
                for d in doctors:
                    knowledge_matrix += f"  * Provider: {d['name']} ({d['specialization']}) | Location: {d['location']} | Phone: {d['contact']}\n"

        try:
            system_instruction = (
                "You are an elite clinical assistant for the SkinSense web platform.\n\n"
                "CRITICAL INSTRUCTIONS:\n"
                "1. Output your answer strictly using beautifully structured clean HTML fragments suitable for a narrow chat widget.\n"
                "2. Do NOT use markdown code blocks like ```html. Output raw HTML directly.\n"
                "3. Print your response matching this exact layout wrapper structural format:\n"
                "   <div class='chat-result-card'>"
                "     <div class='result-badge'>Condition Profile: (Disease Name)</div>"
                "     <div class='result-section'>"
                "       <h6><i class='fas fa-capsules me-2 text-primary'></i>Recommended Care Products</h6>"
                "       <div class='d-flex flex-wrap gap-1' style='margin-top: 5px;'><span class='badge bg-light text-dark border'>(Product 1)</span></div>"
                "     </div>"
                "     <div class='result-section'>"
                "       <h6><i class='fas fa-user-md me-2 text-success'></i>Available Specialists</h6>"
                "       <div class='doc-item'><strong>Dr. Name</strong> (Specialization)<br><small class='text-muted'><i class='fas fa-phone me-1'></i>Phone | <i class='fas fa-map-marker-alt me-1'></i>Location</small></div>"
                "     </div>"
                "   </div>\n"
                "4. Keep entries concise, extract precise names from data matching the query, and under no circumstances generate hyperlinks or markdown links.\n"
                "5. If multiple profiles match a general query, rotate or select a representative condition from the database to highlight."
            )
            
            full_prompt = f"{system_instruction}\n\n{knowledge_matrix}\n\nPatient Query: {message}"
            
            response = ai_model.generate_content(full_prompt)
            if response and response.text:
                clean_reply = response.text.replace("```html", "").replace("```", "").strip()
                return JsonResponse({"reply": clean_reply})
            else:
                raise Exception("Empty response pool.")

        # --- 2. PIPELINE B: LOCAL MULTI-MATCH RANDOMIZED FALLBACK MODE (API EXPIRED) ---
        except Exception as api_error:
            print(f"Gemini API offline/expired. Running randomized query lookup matrix: {api_error}")
            
            # Keep track of ALL matching conditions found for this query pool
            valid_matches = []
            
            for disease in all_diseases:
                search_pool = disease.lower() + " " + DISEASE_DESCRIPTIONS.get(disease, "").lower()
                search_pool += " " + " ".join(DISEASE_SYMPTOMS.get(disease, [])).lower()
                
                products = PRODUCTS_DATA.get(disease, [])
                search_pool += " " + " ".join([p["name"].lower() for p in products])
                
                doc_entry = next((d for d in DOCTORS_DATA if d["disease"].lower() == disease.lower()), None)
                if doc_entry:
                    for d in doc_entry["doctors"]:
                        search_pool += f" {d['name'].lower()} {d['specialization'].lower()} {d['location'].lower()}"
                
                # If match found, push it into our valid pool list
                if message_lower in search_pool or any(word in search_pool for word in message_lower.split() if len(word) > 3):
                    valid_matches.append(disease)

            # --- DYNAMIC RANDOM SELECTION BLOCK ---
            # If the user typed a broad keyword (e.g. 'doctor' or 'sangamner'), valid_matches will contain multiple options.
            # random.choice() ensures it highlights a different skin condition profile every time they search.
            if valid_matches:
                matched_disease = random.choice(valid_matches)
            else:
                # Total fallback: if completely unrecognized, pick a random disease from your arrays to educate the user
                matched_disease = random.choice(all_diseases)

            # --- STRUCTURED HTML GENERATION ENGINE ---
            products = PRODUCTS_DATA.get(matched_disease, [])
            prod_html = "".join([f"<span class='badge bg-light text-dark border me-1 mb-1'>{p['name']}</span>" for p in products])
            
            doc_entry = next((d for d in DOCTORS_DATA if d["disease"].lower() == matched_disease.lower()), None)
            doc_html = ""
            if doc_entry and doc_entry.get("doctors"):
                for d in doc_entry["doctors"]:
                    doc_html += f"""
                    <div class='doc-item mb-2 pb-2' style='border-bottom: 1px dashed var(--border-color);'>
                        <strong>{d['name']}</strong> <span class='small text-muted'>({d['specialization']})</span><br>
                        <small class='text-muted d-block mt-1'><i class='fas fa-phone text-success me-1'></i>{d['contact']}</small>
                        <small class='text-muted d-block'><i class='fas fa-map-marker-alt text-danger me-1'></i>{d['location']}</small>
                    </div>"""
            else:
                doc_html = "<p class='small text-muted m-0'>No specific local doctor entries listed.</p>"

            fallback_html = f"""
            <div class='chat-result-card w-100'>
                <div class='result-badge mb-3'>Condition Profile: {matched_disease}</div>
                <div class='result-section mb-3'>
                    <h6 class='fw-bold mb-2' style='font-size:0.9rem; color:var(--skin-secondary);'><i class='fas fa-capsules me-2'></i>Recommended Care Products</h6>
                    <div class='d-flex flex-wrap'>{prod_html}</div>
                </div>
                <div class='result-section'>
                    <h6 class='fw-bold mb-2' style='font-size:0.9rem; color:var(--skin-secondary);'><i class='fas fa-user-md me-2'></i>Available Specialists</h6>
                    <div>{doc_html}</div>
                </div>
                <div class='text-center mt-2 text-muted' style='font-size: 9px; opacity: 0.7;'>
                    <i class='fas fa-sync me-1'></i>local chatbot assistant.
                </div>
            </div>"""
            return JsonResponse({"reply": fallback_html})

    except Exception as general_error:
        return JsonResponse({"reply": f"An error occurred: {str(general_error)}"}, status=500)
# message send 

def contact(request):
    """
    Saves the contact message to the Database (Admin Panel).
    """
    if request.method == 'POST':
        # Get data from the form
        name = request.POST.get('name')
        user_email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        try:
            # Create and save the message to the database
            ContactMessage.objects.create(
                name=name,
                email=user_email,
                subject=subject,
                message=message
            )
            messages.success(request, "Your message has been sent successfully!")
        except Exception as e:
            messages.error(request, f"Error saving message: {e}")
            
        return redirect('contact')

    return render(request, 'contact.html')

@login_required
def account(request):
    """ Displays user profile and allows updating details """
    user = request.user
    
    if request.method == 'POST':
        # Get data from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        # Update User Object
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        messages.success(request, "Profile updated successfully! ✅")
        return redirect('account')

    context = {
        'user': user,
        'joined_date': user.date_joined.strftime("%B %d, %Y")
    }
    return render(request, 'account.html', context)
# --- ADD THESE IMPORTS AT THE TOP OF app/views.py ---
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

# --- REPLACE THE OLD 'settings' FUNCTION WITH THIS ---
@login_required
def settings(request):
    """ Handles Password Change and Account Deletion """
    user = request.user
    password_form = PasswordChangeForm(user)

    if request.method == 'POST':
        # 1. HANDLE PASSWORD CHANGE
        if 'change_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keeps user logged in
                messages.success(request, 'Your password was successfully updated! ')
                return redirect('settings')
            else:
                messages.error(request, 'Please correct the error below.')
        
        # 2. HANDLE ACCOUNT DELETION
        elif 'delete_account' in request.POST:
            user.delete()
            messages.success(request, "Your account has been deleted. We are sorry to see you go.")
            return redirect('index')

    return render(request, 'settings.html', {'password_form': password_form})
@login_required
def history(request):
    """
    Fetches all past records for the logged-in user.
    """
    # SECURITY FIX: Prevent Doctors from accessing the Patient History page
    # If the user has a 'doctor' attribute, they are a doctor and should be redirected
    if hasattr(request.user, 'doctor'):
        messages.warning(request, "Doctors must use the specialized Doctor Dashboard.")
        return redirect('dashboards')

    # 1. Fetch MRI Scans (Image based)
    # We use 'filter(user=request.user)' so users only see THEIR own data
    mri_records = MRIPatientData.objects.filter(user=request.user).order_by('-id')

    # 2. Fetch Symptom Checks (Text based)
    symptom_records = PatientSkinData.objects.filter(user=request.user).order_by('-id')

    context = {
        'mri_records': mri_records,
        'symptom_records': symptom_records
    }
    return render(request, 'history.html', context)

@login_required
def delete_mri(request, record_id):
    record = get_object_or_404(MRIPatientData, id=record_id, user=request.user)
    record.delete()
    messages.success(request, "MRI record deleted successfully.")
    return redirect('history')

@login_required
def delete_symptom(request, record_id):
    record = get_object_or_404(PatientSkinData, id=record_id, user=request.user)
    record.delete()
    messages.success(request, "Symptom report deleted successfully.")
    return redirect('history')


@login_required
def bulk_delete_mri(request):
    if request.method == "POST":
        record_ids = request.POST.getlist('record_ids')
        if record_ids:
            deleted, _ = MRIPatientData.objects.filter(id__in=record_ids, user=request.user).delete()
            messages.success(request, f"Deleted {deleted} MRI records.")
    return redirect('history')

@login_required
def bulk_delete_symptoms(request):
    if request.method == "POST":
        record_ids = request.POST.getlist('record_ids')
        if record_ids:
            # Note: Ensure PatientSkinData model also has a 'user' field
            deleted, _ = PatientSkinData.objects.filter(id__in=record_ids, user=request.user).delete()
            messages.success(request, f"Deleted {deleted} symptom reports.")
    return redirect('history')