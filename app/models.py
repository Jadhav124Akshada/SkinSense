from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from doctor.models import Doctor

class PatientSkinData(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
    ]
    # Patient Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    contact = models.CharField(max_length=15)

    # Symptoms
    SYMPTOM_CHOICES = [
        ('0', 'Itching'),
        ('1', 'Redness'),
        ('2', 'Rash'),
        ('3', 'Scaling'),
        ('4', 'Blister'),
        ('5', 'Pus Filled'),
        ('6', 'Pain'),
        ('7', 'Dry Skin'),
        ('8', 'Swelling'),
        ('9', 'Burning'),
        ('10', 'Cracks'),
        ('11', 'Circular Rash'),
        ('12', 'Oozing'),
        ('13', 'Fever'),
        ('14', 'Hair Loss'),
        ('15', 'Dark Spot'),
        ('16', 'Numbness'),
        ('17', 'Ulcer'),
        ('18', 'Peeling'),
        ('19', 'Thickness'),
    ]

    sym1 = models.CharField(max_length=20, choices=SYMPTOM_CHOICES)
    sym2 = models.CharField(max_length=20, choices=SYMPTOM_CHOICES)
    sym3 = models.CharField(max_length=20, choices=SYMPTOM_CHOICES)
    sym4 = models.CharField(max_length=20, choices=SYMPTOM_CHOICES, blank=True, null=True)
    sym5 = models.CharField(max_length=20, choices=SYMPTOM_CHOICES, blank=True, null=True)
    sym6 = models.CharField(max_length=20, choices=SYMPTOM_CHOICES, blank=True, null=True)
    sym7 = models.CharField(max_length=20, choices=SYMPTOM_CHOICES, blank=True, null=True)
    sym8 = models.CharField(max_length=20, choices=SYMPTOM_CHOICES, blank=True, null=True)
    sym9 = models.CharField(max_length=20, choices=SYMPTOM_CHOICES, blank=True, null=True)
    sym10 = models.CharField(max_length=20, choices=SYMPTOM_CHOICES, blank=True, null=True)

    # Predicted Disease
    predicted_disease = models.CharField(max_length=100, blank=True, null=True)
    
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    # Timestamp
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.predicted_disease or 'Not Predicted'}"


class MRIPatientData(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    age = models.IntegerField()
    mobile = models.CharField(max_length=15)
    predicted_disease = models.CharField(max_length=200, blank=True, null=True)
    confidence = models.FloatField(blank=True, null=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")  # ✅ Added
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='mri_scans/', blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.fname} {self.lname} ({self.predicted_disease})"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"