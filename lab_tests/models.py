from django.db import models
from django.contrib.auth import get_user_model
from patients.models import Patient
from decimal import Decimal

User = get_user_model()


class LabTestCategory(models.Model):
    """
    Categories for lab tests (e.g., Blood Test, Urine Test, X-Ray)
    """
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lab_test_categories'
        verbose_name = 'Lab Test Category'
        verbose_name_plural = 'Lab Test Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class LabTest(models.Model):
    """
    Lab test types/templates
    """
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
    
    test_name = models.CharField(max_length=200)
    category = models.ForeignKey(LabTestCategory, on_delete=models.PROTECT, related_name='tests')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_tests')
    ordered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ordered_tests')
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='performed_tests')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='routine')
    
    # Test details
    test_code = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    
    # Dates
    ordered_date = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateTimeField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    
    # Results
    results = models.TextField(blank=True, null=True)
    normal_range = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Cost
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lab_tests'
        verbose_name = 'Lab Test'
        verbose_name_plural = 'Lab Tests'
        ordering = ['-ordered_date']
    
    def __str__(self):
        return f"{self.test_name} - {self.patient.full_name}"


class LabTestResult(models.Model):
    """
    Individual test results/parameters for a lab test
    """
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE, related_name='test_results')
    parameter_name = models.CharField(max_length=200)
    value = models.CharField(max_length=200)
    unit = models.CharField(max_length=50, blank=True, null=True)
    normal_range = models.CharField(max_length=200, blank=True, null=True)
    is_abnormal = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'lab_test_results'
        verbose_name = 'Lab Test Result'
        verbose_name_plural = 'Lab Test Results'
        ordering = ['parameter_name']
    
    def __str__(self):
        return f"{self.parameter_name}: {self.value} {self.unit or ''}"
