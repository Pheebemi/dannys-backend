from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import SystemSettings
from .serializers import SystemSettingsSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_settings_view(request):
    """
    Get system settings
    GET /api/settings/
    """
    # Check if user is admin
    if request.user.role != 'admin' and not request.user.is_superuser:
        return Response({
            'success': False,
            'message': 'Permission denied. Admin access required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    settings = SystemSettings.get_settings()
    serializer = SystemSettingsSerializer(settings)
    return Response({
        'success': True,
        'settings': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_settings_view(request):
    """
    Update system settings
    PUT/PATCH /api/settings/update/
    """
    # Check if user is admin
    if request.user.role != 'admin' and not request.user.is_superuser:
        return Response({
            'success': False,
            'message': 'Permission denied. Admin access required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    settings = SystemSettings.get_settings()
    serializer = SystemSettingsSerializer(settings, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save(updated_by=request.user)
        return Response({
            'success': True,
            'message': 'Settings updated successfully',
            'settings': serializer.data
        }, status=status.HTTP_200_OK)
    
    # Return detailed error messages
    error_messages = []
    for field, errors in serializer.errors.items():
        if isinstance(errors, list):
            error_messages.extend([f"{field}: {error}" for error in errors])
        else:
            error_messages.append(f"{field}: {errors}")
    
    return Response({
        'success': False,
        'message': 'Failed to update settings',
        'errors': serializer.errors,
        'error': '; '.join(error_messages) if error_messages else 'Invalid data'
    }, status=status.HTTP_400_BAD_REQUEST)

