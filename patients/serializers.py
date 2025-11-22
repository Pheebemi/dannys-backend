from rest_framework import serializers
from .models import Patient
from django.contrib.auth import get_user_model

User = get_user_model()


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model"""
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    created_by_name = serializers.SerializerMethodField()
    assigned_doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = (
            'id', 'first_name', 'last_name', 'full_name', 'date_of_birth', 'age',
            'gender', 'blood_type', 'email', 'phone_number', 'address', 'city',
            'state', 'zip_code', 'country', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relationship',
            'allergies', 'medical_conditions', 'medications', 'insurance_provider',
            'insurance_policy_number', 'notes', 'is_active', 'assigned_doctor',
            'assigned_doctor_name', 'created_at', 'updated_at', 'created_by', 'created_by_name'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.full_name or obj.created_by.username
        return None
    
    def get_assigned_doctor_name(self, obj):
        if obj.assigned_doctor:
            return obj.assigned_doctor.full_name or obj.assigned_doctor.username
        return None


class PatientCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new patient"""
    
    class Meta:
        model = Patient
        fields = (
            'first_name', 'last_name', 'date_of_birth', 'gender', 'blood_type',
            'email', 'phone_number', 'address', 'city', 'state', 'zip_code',
            'country', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'allergies', 'medical_conditions',
            'medications', 'insurance_provider', 'insurance_policy_number', 
            'notes', 'assigned_doctor'
        )
    
    def validate_email(self, value):
        """Validate email uniqueness if provided"""
        if value:
            if Patient.objects.filter(email=value).exists():
                raise serializers.ValidationError("A patient with this email already exists.")
        return value
    
    def validate_phone_number(self, value):
        """Validate phone number is provided"""
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        return value

