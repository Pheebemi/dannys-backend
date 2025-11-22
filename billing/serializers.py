from rest_framework import serializers
from .models import Invoice, InvoiceItem, Payment, Service
from patients.models import Patient
from django.contrib.auth import get_user_model

User = get_user_model()


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service model"""
    
    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for InvoiceItem model"""
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = InvoiceItem
        fields = ('id', 'service', 'service_name', 'description', 'quantity', 'unit_price', 'total')
        read_only_fields = ('id', 'total')


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model"""
    processed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = ('id', 'invoice', 'amount', 'payment_method', 'payment_date', 
                  'reference_number', 'notes', 'processed_by', 'processed_by_name', 'created_at')
        read_only_fields = ('id', 'created_at', 'processed_by')
    
    def get_processed_by_name(self, obj):
        if obj.processed_by:
            return obj.processed_by.full_name or obj.processed_by.username
        return None


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_email = serializers.CharField(source='patient.email', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone_number', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    items = InvoiceItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Invoice
        fields = (
            'id', 'invoice_number', 'patient', 'patient_name', 'patient_email', 'patient_phone',
            'status', 'invoice_date', 'due_date', 'subtotal', 'tax_rate', 'tax_amount',
            'discount', 'total_amount', 'paid_amount', 'balance', 'notes', 'created_by',
            'created_by_name', 'created_at', 'updated_at', 'items', 'payments'
        )
        read_only_fields = ('id', 'invoice_number', 'created_at', 'updated_at', 'created_by',
                           'subtotal', 'tax_amount', 'total_amount', 'balance', 'status')
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.full_name or obj.created_by.username
        return None


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an invoice"""
    items = InvoiceItemSerializer(many=True, required=False)
    
    class Meta:
        model = Invoice
        fields = (
            'patient', 'invoice_date', 'due_date', 'tax_rate', 'discount', 'notes', 'items'
        )
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        # Create invoice first with default values
        invoice = Invoice.objects.create(**validated_data)
        
        # Create invoice items
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        
        # Recalculate totals after items are added
        from decimal import Decimal
        invoice.subtotal = Decimal(str(sum(item.total for item in invoice.items.all())))
        invoice.save()
        
        return invoice


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a payment"""
    
    class Meta:
        model = Payment
        fields = ('invoice', 'amount', 'payment_method', 'payment_date', 'reference_number', 'notes')

