from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'email', 'date_of_birth', 'gender', 'is_active', 'created_at')
    list_filter = ('gender', 'blood_type', 'is_active', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    fieldsets = (
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
        ('Additional', {
            'fields': ('notes', 'is_active', 'created_by', 'created_at', 'updated_at')
        }),
    )

