from rest_framework import serializers
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone_number', read_only=True)
    patient_email = serializers.CharField(source='patient.email', read_only=True)
    doctor_name = serializers.SerializerMethodField()
    checked_in_by_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'patient_phone', 'patient_email',
            'doctor', 'doctor_name',
            'appointment_date', 'appointment_time', 'duration_minutes',
            'status', 'priority', 'reason', 'notes',
            'checked_in_at', 'checked_in_by', 'checked_in_by_name',
            'completed_at', 'created_by', 'created_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['checked_in_at', 'checked_in_by', 'completed_at', 'created_at', 'updated_at']

    def get_doctor_name(self, obj):
        return obj.doctor.full_name or obj.doctor.username

    def get_checked_in_by_name(self, obj):
        if obj.checked_in_by:
            return obj.checked_in_by.full_name or obj.checked_in_by.username
        return None

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.full_name or obj.created_by.username
        return None
