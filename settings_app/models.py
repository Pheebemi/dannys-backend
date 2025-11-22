from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SystemSettings(models.Model):
    """
    System-wide settings for the clinic
    """
    # Clinic Information
    clinic_name = models.CharField(max_length=200, default="Dannys Wellness Clinic")
    clinic_address = models.TextField(blank=True, null=True)
    clinic_city = models.CharField(max_length=100, blank=True, null=True)
    clinic_state = models.CharField(max_length=100, blank=True, null=True)
    clinic_zip_code = models.CharField(max_length=20, blank=True, null=True)
    clinic_country = models.CharField(max_length=100, default="United States")
    clinic_phone = models.CharField(max_length=20, blank=True, null=True)
    clinic_email = models.EmailField(blank=True, null=True)
    clinic_website = models.URLField(blank=True, null=True)
    
    # Working Hours
    monday_open = models.TimeField(blank=True, null=True)
    monday_close = models.TimeField(blank=True, null=True)
    tuesday_open = models.TimeField(blank=True, null=True)
    tuesday_close = models.TimeField(blank=True, null=True)
    wednesday_open = models.TimeField(blank=True, null=True)
    wednesday_close = models.TimeField(blank=True, null=True)
    thursday_open = models.TimeField(blank=True, null=True)
    thursday_close = models.TimeField(blank=True, null=True)
    friday_open = models.TimeField(blank=True, null=True)
    friday_close = models.TimeField(blank=True, null=True)
    saturday_open = models.TimeField(blank=True, null=True)
    saturday_close = models.TimeField(blank=True, null=True)
    sunday_open = models.TimeField(blank=True, null=True)
    sunday_close = models.TimeField(blank=True, null=True)
    
    # System Configuration
    appointment_duration_minutes = models.IntegerField(default=30)
    max_appointments_per_day = models.IntegerField(default=50)
    allow_online_booking = models.BooleanField(default=True)
    require_email_verification = models.BooleanField(default=False)
    
    # Notification Settings
    email_notifications_enabled = models.BooleanField(default=True)
    sms_notifications_enabled = models.BooleanField(default=False)
    appointment_reminder_hours = models.IntegerField(default=24)
    
    # Security Settings
    session_timeout_minutes = models.IntegerField(default=30)
    password_reset_enabled = models.BooleanField(default=True)
    two_factor_auth_enabled = models.BooleanField(default=False)
    
    # Backup Settings
    auto_backup_enabled = models.BooleanField(default=True)
    backup_frequency_days = models.IntegerField(default=7)
    last_backup_date = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='settings_updated')
    
    class Meta:
        db_table = 'system_settings'
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'
    
    def __str__(self):
        return f"System Settings - {self.clinic_name}"
    
    @classmethod
    def get_settings(cls):
        """Get or create system settings singleton"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

