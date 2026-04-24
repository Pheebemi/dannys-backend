from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'full_name', 
                  'role', 'phone_number', 'profile_picture', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at', 'is_active')


class LoginSerializer(serializers.Serializer):
    """Serializer for login — role is optional (auto-detected from user record)"""
    email = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(write_only=True, required=True, allow_blank=False)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False, allow_null=True)

    def validate(self, attrs):
        email = attrs.get('email', '').lower().strip()
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'Invalid email or password.'})

        if not user.check_password(password):
            raise serializers.ValidationError({'password': 'Invalid email or password.'})

        if not user.is_active:
            raise serializers.ValidationError({'email': 'This account has been disabled.'})

        attrs['user'] = user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 
                  'first_name', 'last_name', 'role', 'phone_number')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user

