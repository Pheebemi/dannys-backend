from rest_framework import serializers
from .models import VitalSign, MedicationRecord


class VitalSignSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    recorded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = VitalSign
        fields = [
            'id', 'patient', 'patient_name',
            'recorded_by', 'recorded_by_name', 'recorded_at',
            'temperature', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'heart_rate', 'respiratory_rate', 'oxygen_saturation',
            'weight', 'height', 'bmi', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['bmi', 'created_at', 'updated_at']

    def get_recorded_by_name(self, obj):
        if obj.recorded_by:
            return obj.recorded_by.full_name or obj.recorded_by.username
        return None


class MedicationRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    administered_by_name = serializers.SerializerMethodField()

    class Meta:
        model = MedicationRecord
        fields = [
            'id', 'patient', 'patient_name',
            'medication_name', 'dosage', 'frequency', 'route',
            'prescribed_by', 'scheduled_time',
            'administered_at', 'administered_by', 'administered_by_name',
            'status', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_administered_by_name(self, obj):
        if obj.administered_by:
            return obj.administered_by.full_name or obj.administered_by.username
        return None
