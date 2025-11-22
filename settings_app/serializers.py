from rest_framework import serializers
from .models import SystemSettings
from django.contrib.auth import get_user_model

User = get_user_model()


class SystemSettingsSerializer(serializers.ModelSerializer):
    """Serializer for SystemSettings model"""
    updated_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemSettings
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'updated_by')
    
    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return obj.updated_by.full_name or obj.updated_by.username
        return None

