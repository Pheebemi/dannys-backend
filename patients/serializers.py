from rest_framework import serializers
from .models import Patient, HMO
from django.contrib.auth import get_user_model

User = get_user_model()


class HMOSerializer(serializers.ModelSerializer):
    class Meta:
        model = HMO
        fields = ['id', 'name', 'code', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class PatientSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    created_by_name = serializers.SerializerMethodField()
    assigned_doctor_name = serializers.SerializerMethodField()
    hmo_name = serializers.SerializerMethodField()
    patient_type_display = serializers.CharField(source='get_patient_type_display', read_only=True)

    class Meta:
        model = Patient
        fields = (
            'id', 'patient_code', 'first_name', 'last_name', 'full_name', 'date_of_birth', 'age',
            'gender', 'blood_type', 'email', 'phone_number', 'address', 'city',
            'state', 'zip_code', 'country',
            'patient_type', 'patient_type_display', 'hmo', 'hmo_name',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'allergies', 'medical_conditions', 'medications',
            'insurance_provider', 'insurance_policy_number',
            'notes', 'is_active', 'assigned_doctor', 'assigned_doctor_name',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
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

    def get_hmo_name(self, obj):
        return obj.hmo.name if obj.hmo else None


class PatientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = (
            'first_name', 'last_name', 'date_of_birth', 'gender', 'blood_type',
            'email', 'phone_number', 'address', 'city', 'state', 'zip_code', 'country',
            'patient_type', 'hmo',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'allergies', 'medical_conditions', 'medications',
            'insurance_provider', 'insurance_policy_number',
            'notes', 'assigned_doctor',
        )

    def validate_email(self, value):
        if value:
            if Patient.objects.filter(email=value).exists():
                raise serializers.ValidationError("A patient with this email already exists.")
        return value

    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        return value

    def validate(self, data):
        if data.get('patient_type') == 'retainership' and not data.get('hmo'):
            raise serializers.ValidationError({'hmo': 'HMO is required for Retainership patients.'})
        return data
