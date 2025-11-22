from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from patients.models import Patient

User = get_user_model()


class Service(models.Model):
    """
    Medical services that can be billed
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'services'
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - ${self.price}"


class Invoice(models.Model):
    """
    Invoice/Bill for patient services
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    invoice_date = models.DateField()
    due_date = models.DateField()
    
    # Financial
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Additional info
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='invoices_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-invoice_date', '-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.patient.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate invoice number
            last_invoice = Invoice.objects.order_by('-id').first()
            if last_invoice:
                last_num = int(last_invoice.invoice_number.split('-')[-1]) if '-' in last_invoice.invoice_number else 0
                self.invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{last_num + 1:04d}"
            else:
                from django.utils import timezone
                self.invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-0001"
        
        # Ensure all values are Decimal for calculations
        subtotal = Decimal(str(self.subtotal))
        discount = Decimal(str(self.discount))
        tax_rate = Decimal(str(self.tax_rate))
        paid_amount = Decimal(str(self.paid_amount))
        
        # Calculate totals
        after_discount = subtotal - discount
        self.tax_amount = after_discount * (tax_rate / Decimal('100'))
        self.total_amount = after_discount + self.tax_amount
        self.balance = self.total_amount - paid_amount
        
        # Update status based on payment
        if self.balance <= 0 and paid_amount > 0:
            self.status = 'paid'
        elif paid_amount > 0 and self.balance > 0:
            self.status = 'partial'
        elif paid_amount == 0 and self.status != 'draft':
            self.status = 'pending'
        
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    """
    Individual line items on an invoice
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    description = models.CharField(max_length=500, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'invoice_items'
        verbose_name = 'Invoice Item'
        verbose_name_plural = 'Invoice Items'
    
    def __str__(self):
        return f"{self.service.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Update invoice subtotal
        self.invoice.subtotal = sum(item.total for item in self.invoice.items.all())
        self.invoice.save()


class Payment(models.Model):
    """
    Payment records for invoices
    """
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('insurance', 'Insurance'),
        ('other', 'Other'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    payment_date = models.DateField()
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='payments_processed')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date', '-created_at']
    
    def __str__(self):
        return f"Payment of ${self.amount} for {self.invoice.invoice_number}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update invoice paid amount
        self.invoice.paid_amount = sum(payment.amount for payment in self.invoice.payments.all())
        self.invoice.save()

