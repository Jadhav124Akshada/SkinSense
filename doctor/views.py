from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Doctor
from app.models import PatientSkinData, MRIPatientData
from django.db.models import Q

# --- CONSTANTS ---
SYMPTOM_INDEX_MAP = {
    "0": "Itching", "1": "Redness", "2": "Rash", "3": "Scaling",
    "4": "Blister", "5": "Pus Filled", "6": "Pain", "7": "Dry Skin",
    "8": "Swelling", "9": "Burning", "10": "Cracks", "11": "Circular Rash",
    "12": "Oozing", "13": "Fever", "14": "Hair Loss", "15": "Dark Spot",
    "16": "Numbness", "17": "Ulcer", "18": "Peeling", "19": "Thickness"
}

# --- AUTHENTICATION ---

def index1(request):
    return render(request, "index1.html")

def doctor_register(request):
    if request.method == "POST":
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        username = request.POST.get('username')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        specialization = request.POST.get('specialization')
        contact = request.POST.get('contact')
        location = request.POST.get('location')

        if password != cpassword:
            messages.error(request, "Passwords do not match!")
            return redirect("doctor_register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("doctor_register")

        user = User.objects.create_user(username=username, password=password, first_name=fname, last_name=lname)
        user.save()

        Doctor.objects.create(user=user, specialization=specialization, contact=contact, location=location)

        messages.success(request, "Doctor account created successfully.")
        return redirect("doctor_login")

    return render(request, "doctor_register.html")

def doctor_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            if hasattr(user, 'doctor'):
                # Force logout any existing patient session before logging in as doctor
                if request.user.is_authenticated:
                    logout(request)
                
                login(request, user)
                messages.success(request, "Doctor Login Successful!")
                return redirect("dashboards")
            else:
                messages.error(request, "This account is not registered as a doctor.")
        else:
            messages.error(request, "Invalid Username or Password.")
            
    return render(request, "doctor_login.html")

def doctor_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("doctor_login")

# --- DASHBOARD & FEATURES ---

@login_required
def dashboards(request):
    # SECURITY FIX: Ensure the user is actually a doctor
    if not hasattr(request.user, 'doctor'):
        messages.error(request, "Access Denied. Patients cannot access the Doctor Dashboard.")
        return redirect('index')

    doctor = request.user.doctor

    # Handle Accept/Reject Actions (POST)
    if request.method == "POST":
        patient_id = request.POST.get("patient_id")
        action = request.POST.get("action")
        patient_type = request.POST.get("patient_type")

        if patient_type == "skin":
            patient = get_object_or_404(PatientSkinData, id=patient_id, doctor=doctor)
        elif patient_type == "mri":
            patient = get_object_or_404(MRIPatientData, id=patient_id, doctor=doctor)
        else:
            return redirect("dashboards")

        if action == "accept":
            patient.status = "Accepted"
        elif action == "reject":
            patient.status = "Rejected"
        
        patient.save()
        return redirect("dashboards")

    # SEARCH LOGIC (GET)
    query = request.GET.get('q')
    
    # Start with initial querysets filtered by doctor
    skin_patients = PatientSkinData.objects.filter(doctor=doctor).order_by('-date')
    mri_patients = MRIPatientData.objects.filter(doctor=doctor).order_by('-created_at')

    # Apply filtering if a search query exists
    if query:
        skin_patients = skin_patients.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) |
            Q(id__icontains=query)
        )
        mri_patients = mri_patients.filter(
            Q(fname__icontains=query) | 
            Q(lname__icontains=query) | 
            Q(id__icontains=query)
        )

    # Calculate stats based on results
    all_patients_list = list(skin_patients) + list(mri_patients)

    context = {
        "skin_patients": skin_patients,
        "mri_patients": mri_patients,
        "total_patients": len(all_patients_list),
        "pending_count": sum(1 for p in all_patients_list if p.status == "Pending"),
        "accepted_count": sum(1 for p in all_patients_list if p.status == "Accepted"),
        "rejected_count": sum(1 for p in all_patients_list if p.status == "Rejected"),
        "doctor": doctor,
        "query": query,
    }
    return render(request, "dashboards.html", context)

@login_required
def doctor_patient_detail(request, id):
    patient = get_object_or_404(PatientSkinData, id=id)
    readable_symptoms = []
    for i in range(1, 11):
        val = getattr(patient, f"sym{i}")
        if val and val != "default":
            readable_symptoms.append(SYMPTOM_INDEX_MAP.get(str(val), val) if str(val).isdigit() else val)

    return render(request, 'doctor_patient_detail.html', {'patient': patient, 'symptoms': readable_symptoms})

@login_required
def doctor_mri_detail(request, id):
    patient = get_object_or_404(MRIPatientData, id=id)
    return render(request, 'doctor_mri_detail.html', {'patient': patient})

@login_required
def doctor_account(request):
    try:
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        logout(request)
        return redirect("doctor_login")

    if request.method == "POST":
        doctor.user.first_name = request.POST.get('fname')
        doctor.user.last_name = request.POST.get('lname')
        doctor.specialization = request.POST.get('specialization')
        doctor.contact = request.POST.get('contact')
        doctor.location = request.POST.get('location')
        doctor.user.save()
        doctor.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("doctor_account")
    
    return render(request, "doctor_account.html", {"doctor": doctor})

@login_required
def doctor_settings(request):
    try:
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        logout(request)
        return redirect("doctor_login")

    if request.method == "POST":
        old_pass = request.POST.get('old_password')
        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')

        if not request.user.check_password(old_pass):
            messages.error(request, "Incorrect current password.")
        elif new_pass != confirm_pass:
            messages.error(request, "New passwords do not match.")
        else:
            request.user.set_password(new_pass)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Password updated successfully!")
            return redirect("dashboards")
            
    return render(request, "doctor_settings.html", {"doctor": doctor})