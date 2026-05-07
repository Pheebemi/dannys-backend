from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from patients.models import Patient

User = get_user_model()


class VitalSign(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vital_signs')
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='vital_signs_recorded')
    recorded_at = models.DateTimeField(default=None, null=True, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True)
    heart_rate = models.PositiveIntegerField(null=True, blank=True)
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True)
    oxygen_saturation = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    bmi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vital_signs'
        ordering = ['-recorded_at']

    def __str__(self):
        return f"Vitals for {self.patient.full_name} at {self.recorded_at}"

    def save(self, *args, **kwargs):
        if not self.recorded_at:
            self.recorded_at = timezone.now()
        if self.weight and self.height and self.height > 0:
            height_m = float(self.height) / 100
            self.bmi = round(float(self.weight) / (height_m ** 2), 2)
        super().save(*args, **kwargs)


class MedicationRecord(models.Model):
    ROUTE_CHOICES = [
        ('oral', 'Oral'),
        ('intravenous', 'Intravenous'),
        ('intramuscular', 'Intramuscular'),
        ('subcutaneous', 'Subcutaneous'),
        ('topical', 'Topical'),
        ('inhalation', 'Inhalation'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('administered', 'Administered'),
        ('missed', 'Missed'),
        ('cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medication_records')
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    route = models.CharField(max_length=20, choices=ROUTE_CHOICES, default='oral')
    prescribed_by = models.CharField(max_length=200, blank=True, null=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    administered_at = models.DateTimeField(null=True, blank=True)
    administered_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='medications_administered'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medication_records'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.medication_name} for {self.patient.full_name}"
