from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with role-based access control
    """
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('admin', 'Administrator'),
        ('receptionist', 'Receptionist'),
        ('pharmacist', 'Pharmacist'),
        ('lab_technician', 'Lab Technician'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='receptionist')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

