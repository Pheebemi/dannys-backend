from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from patients.models import Patient

User = get_user_model()


class Prescription(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ready', 'Ready for Pickup'),
        ('dispensed', 'Dispensed'),
        ('cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    prescribed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='prescriptions_written', limit_choices_to={'role': 'doctor'}
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    prescription_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    dispensed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='prescriptions_dispensed'
    )
    dispensed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'prescriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Prescription for {self.patient.full_name} ({self.get_status_display()})"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration_days = models.PositiveIntegerField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    refills_remaining = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, null=True)
    inventory_item = models.ForeignKey(
        'MedicationInventory', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='dispensed_items'
    )
    out_of_stock = models.BooleanField(default=False)

    class Meta:
        db_table = 'prescription_items'

    def __str__(self):
        return f"{self.medication_name} ({self.dosage})"


class MedicationInventory(models.Model):
    UNIT_CHOICES = [
        ('tablets', 'Tablets'),
        ('capsules', 'Capsules'),
        ('ml', 'Milliliters (ml)'),
        ('vials', 'Vials'),
        ('sachets', 'Sachets'),
        ('patches', 'Patches'),
        ('other', 'Other'),
    ]

    medication_name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='tablets')
    stock_quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    supplier = models.CharField(max_length=200, blank=True, null=True)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medication_inventory'
        ordering = ['medication_name']

    def __str__(self):
        return f"{self.medication_name} ({self.stock_quantity} {self.unit})"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level
