from rest_framework import serializers
from .models import LabTest, LabTestCategory, LabTestResult
from patients.models import Patient
from django.contrib.auth import get_user_model

User = get_user_model()


class LabTestCategorySerializer(serializers.ModelSerializer):
    """Serializer for LabTestCategory model"""
    
    class Meta:
        model = LabTestCategory
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class LabTestResultSerializer(serializers.ModelSerializer):
    """Serializer for LabTestResult model"""
    
    class Meta:
        model = LabTestResult
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class LabTestSerializer(serializers.ModelSerializer):
    """Serializer for LabTest model"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_email = serializers.CharField(source='patient.email', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone_number', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    ordered_by_name = serializers.SerializerMethodField()
    performed_by_name = serializers.SerializerMethodField()
    test_results = LabTestResultSerializer(many=True, read_only=True)
    
    class Meta:
        model = LabTest
        fields = (
            'id', 'test_name', 'category', 'category_name', 'patient', 'patient_name',
            'patient_email', 'patient_phone', 'ordered_by', 'ordered_by_name',
            'performed_by', 'performed_by_name', 'status', 'priority', 'test_code',
            'description', 'instructions', 'ordered_date', 'scheduled_date',
            'completed_date', 'results', 'normal_range', 'notes', 'cost',
            'created_at', 'updated_at', 'test_results'
        )
        read_only_fields = ('id', 'ordered_date', 'created_at', 'updated_at')
    
    def get_ordered_by_name(self, obj):
        if obj.ordered_by:
            return obj.ordered_by.full_name or obj.ordered_by.username
        return None
    
    def get_performed_by_name(self, obj):
        if obj.performed_by:
            return obj.performed_by.full_name or obj.performed_by.username
        return None


class LabTestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a lab test"""
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, write_only=True, source='cost')
    
    class Meta:
        model = LabTest
        fields = (
            'test_name', 'category', 'patient', 'ordered_by', 'priority',
            'test_code', 'description', 'instructions', 'scheduled_date',
            'normal_range', 'notes', 'cost', 'price'
        )


class LabTestUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a lab test"""
    
    class Meta:
        model = LabTest
        fields = (
            'status', 'performed_by', 'scheduled_date', 'completed_date',
            'results', 'normal_range', 'notes', 'priority'
        )
