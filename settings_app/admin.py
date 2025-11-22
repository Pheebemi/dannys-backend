from django.contrib import admin
from .models import SystemSettings


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('clinic_name', 'clinic_email', 'clinic_phone', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'updated_by')
    
    fieldsets = (
        ('Clinic Information', {
            'fields': ('clinic_name', 'clinic_address', 'clinic_city', 'clinic_state', 
                      'clinic_zip_code', 'clinic_country', 'clinic_phone', 'clinic_email', 'clinic_website')
        }),
        ('Working Hours - Monday', {
            'fields': ('monday_open', 'monday_close')
        }),
        ('Working Hours - Tuesday', {
            'fields': ('tuesday_open', 'tuesday_close')
        }),
        ('Working Hours - Wednesday', {
            'fields': ('wednesday_open', 'wednesday_close')
        }),
        ('Working Hours - Thursday', {
            'fields': ('thursday_open', 'thursday_close')
        }),
        ('Working Hours - Friday', {
            'fields': ('friday_open', 'friday_close')
        }),
        ('Working Hours - Saturday', {
            'fields': ('saturday_open', 'saturday_close')
        }),
        ('Working Hours - Sunday', {
            'fields': ('sunday_open', 'sunday_close')
        }),
        ('System Configuration', {
            'fields': ('appointment_duration_minutes', 'max_appointments_per_day', 
                      'allow_online_booking', 'require_email_verification')
        }),
        ('Notification Settings', {
            'fields': ('email_notifications_enabled', 'sms_notifications_enabled', 'appointment_reminder_hours')
        }),
        ('Security Settings', {
            'fields': ('session_timeout_minutes', 'password_reset_enabled', 'two_factor_auth_enabled')
        }),
        ('Backup Settings', {
            'fields': ('auto_backup_enabled', 'backup_frequency_days', 'last_backup_date')
        }),
        ('Metadata', {
            'fields': ('updated_by', 'created_at', 'updated_at')
        }),
    )

