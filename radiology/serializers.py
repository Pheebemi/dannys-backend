from rest_framework import serializers
from .models import RadiologyCategory, RadiologyTest


class RadiologyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RadiologyCategory
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['created_at']


class RadiologyTestSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone_number', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    ordered_by_name = serializers.SerializerMethodField()
    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = RadiologyTest
        fields = [
            'id', 'patient', 'patient_name', 'patient_phone',
            'category', 'category_name',
            'ordered_by', 'ordered_by_name',
            'performed_by', 'performed_by_name',
            'test_name', 'status', 'priority',
            'description', 'instructions', 'findings', 'impression', 'notes', 'cost',
            'ordered_date', 'scheduled_date', 'completed_date',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_ordered_by_name(self, obj):
        if obj.ordered_by:
            return obj.ordered_by.full_name or obj.ordered_by.username
        return None

    def get_performed_by_name(self, obj):
        if obj.performed_by:
            return obj.performed_by.full_name or obj.performed_by.username
        return None


class RadiologyTestCreateSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)

    class Meta:
        model = RadiologyTest
        fields = [
            'patient', 'category', 'test_name', 'priority',
            'description', 'instructions', 'notes', 'price', 'ordered_date',
        ]

    def create(self, validated_data):
        price = validated_data.pop('price', None)
        if price is not None:
            validated_data['cost'] = price
        return super().create(validated_data)


class RadiologyTestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RadiologyTest
        fields = [
            'status', 'priority', 'performed_by',
            'findings', 'impression', 'notes', 'cost',
            'scheduled_date', 'completed_date',
        ]
