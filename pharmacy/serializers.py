from rest_framework import serializers
from .models import Prescription, MedicationInventory


class PrescriptionSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone_number', read_only=True)
    prescribed_by_name = serializers.SerializerMethodField()
    dispensed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = [
            'id', 'patient', 'patient_name', 'patient_phone',
            'prescribed_by', 'prescribed_by_name',
            'medication_name', 'dosage', 'frequency', 'duration_days',
            'quantity', 'refills_remaining', 'status', 'notes',
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
