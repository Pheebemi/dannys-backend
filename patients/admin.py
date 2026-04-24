from django.contrib import admin
from .models import Patient, HMO


@admin.register(HMO)
class HMOAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'patient_count', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    readonly_fields = ('code', 'created_at', 'updated_at')

    def patient_count(self, obj):
        return obj.patients.count()
    patient_count.short_description = 'Patients'


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_code', 'full_name', 'patient_type', 'hmo', 'phone_number', 'email', 'is_active', 'created_at')
    list_filter = ('patient_type', 'hmo', 'gender', 'blood_type', 'is_active')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'patient_code')
    readonly_fields = ('patient_code', 'created_at', 'updated_at', 'created_by')
    fieldsets = (
        ('Patient ID', {
            'fields': ('patient_code',)
        }),
        ('Classification', {
            'fields': ('patient_type', 'hmo')
        }),
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'gender', 'blood_type')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number', 'address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Medical Information', {
            'fields': ('allergies', 'medical_conditions', 'medications')
        }),
        ('Insurance', {
            'fields': ('insurance_provider', 'insurance_policy_number')
        }),
        ('Portal Account', {
            'fields': ('user',)
        }),
        ('Additional', {
            'fields': ('assigned_doctor', 'notes', 'is_active', 'created_by', 'created_at', 'updated_at')
        }),
    )
