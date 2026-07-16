from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(PatientSkinData)
admin.site.register( MRIPatientData)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'message','sent_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('sent_at',)

