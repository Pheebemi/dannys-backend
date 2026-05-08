from django.db import models
from django.contrib.auth import get_user_model
from patients.models import Patient

User = get_user_model()


class RadiologyCategory(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'radiology_categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class RadiologyTest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('stat', 'STAT (Immediate)'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='radiology_tests')
    category = models.ForeignKey(RadiologyCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='tests')
    ordered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='radiology_orders')
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='radiology_performed')

    test_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='routine')

    description = models.TextField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    findings = models.TextField(blank=True, null=True)
    impression = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    ordered_date = models.DateField(null=True, blank=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'radiology_tests'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.test_name} — {self.patient.full_name}"
