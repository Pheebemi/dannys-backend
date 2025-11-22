from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Patient(models.Model):
    """
    Patient model for storing patient information
    """
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('unknown', 'Unknown'),
    ]
    
    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    blood_type = models.CharField(max_length=10, choices=BLOOD_TYPE_CHOICES, blank=True, null=True)
    
    # Contact Information
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, default='United States')
    
    # Medical Information
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True, help_text="List any known allergies")
    medical_conditions = models.TextField(blank=True, null=True, help_text="List any existing medical conditions")
    medications = models.TextField(blank=True, null=True, help_text="Current medications")
    
    # Insurance Information
    insurance_provider = models.CharField(max_length=200, blank=True, null=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Additional Information
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    assigned_doctor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_patients',
        limit_choices_to={'role': 'doctor'}
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='patients_created')
    
    class Meta:
        db_table = 'patients'
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

