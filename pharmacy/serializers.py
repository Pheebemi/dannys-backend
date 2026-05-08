from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Prescription, PrescriptionItem, MedicationInventory

User = get_user_model()


class PrescriptionItemSerializer(serializers.ModelSerializer):
    inventory_item_name = serializers.CharField(source='inventory_item.medication_name', read_only=True)

    class Meta:
        model = PrescriptionItem
        fields = [
            'id', 'medication_name', 'dosage', 'frequency',
            'duration_days', 'quantity', 'refills_remaining', 'notes',
            'inventory_item', 'inventory_item_name', 'out_of_stock',
        ]


class PrescriptionSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone_number', read_only=True)
    prescribed_by_name = serializers.SerializerMethodField()
    dispensed_by_name = serializers.SerializerMethodField()
    items = PrescriptionItemSerializer(many=True, read_only=True)

    class Meta:
        model = Prescription
        fields = [
            'id', 'patient', 'patient_name', 'patient_phone',
            'prescribed_by', 'prescribed_by_name',
            'status', 'prescription_date', 'notes', 'items',
            'dispensed_by', 'dispensed_by_name', 'dispensed_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['dispensed_by', 'dispensed_at', 'created_at', 'updated_at']

    def get_prescribed_by_name(self, obj):
        if obj.prescribed_by:
            return obj.prescribed_by.full_name or obj.prescribed_by.username
        return None

    def get_dispensed_by_name(self, obj):
        if obj.dispensed_by:
            return obj.dispensed_by.full_name or obj.dispensed_by.username
        return None


class PrescriptionCreateSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True)
    prescribed_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Prescription
        fields = ['patient', 'prescribed_by', 'prescription_date', 'notes', 'items']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("A prescription must have at least one medication.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        prescription = Prescription.objects.create(**validated_data)
        for item in items_data:
            PrescriptionItem.objects.create(prescription=prescription, **item)
        return prescription


class MedicationInventorySerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = MedicationInventory
        fields = [
            'id', 'medication_name', 'generic_name', 'category',
            'unit', 'stock_quantity', 'reorder_level', 'supplier',
            'cost_per_unit', 'selling_price', 'expiry_date',
            'is_active', 'is_low_stock', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
