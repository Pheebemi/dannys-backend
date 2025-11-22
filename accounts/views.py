from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Q
from .serializers import UserSerializer, LoginSerializer, RegisterSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login endpoint
    POST /api/auth/login/
    Body: { "email": "...", "password": "...", "role": "doctor|nurse|admin|..." }
    """
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
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
        'message': 'Login failed',
        'errors': serializer.errors,
        'error': '; '.join(error_messages) if error_messages else 'Invalid credentials'
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout endpoint
    POST /api/auth/logout/
    Header: Authorization: Bearer <access_token>
    Body: { "refresh": "..." }
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'success': True,
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Error during logout',
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Get current user profile
    GET /api/auth/profile/
    Header: Authorization: Bearer <access_token>
    """
    serializer = UserSerializer(request.user)
    return Response({
        'success': True,
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """
    Update current user profile
    PUT/PATCH /api/auth/profile/
    Header: Authorization: Bearer <access_token>
    """
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Refresh access token
    POST /api/auth/refresh/
    Body: { "refresh": "..." }
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({
                'success': False,
                'message': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = RefreshToken(refresh_token)
        return Response({
            'success': True,
            'access': str(token.access_token)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Invalid refresh token',
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


# Admin endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def staff_list_view(request):
    """
    Get list of all staff members
    GET /api/auth/staff/
    Query params: role, search, page, page_size
    """
    # Check if user is admin
    if request.user.role != 'admin' and not request.user.is_superuser:
        return Response({
            'success': False,
            'message': 'Permission denied. Admin access required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    role = request.query_params.get('role')
    search = request.query_params.get('search', '')
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    
    queryset = User.objects.all().order_by('-created_at')
    
    # Filter by role
    if role:
        queryset = queryset.filter(role=role)
    
    # Search functionality
    if search:
        queryset = queryset.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Pagination
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    staff = queryset[start:end]
    
    serializer = UserSerializer(staff, many=True)
    
    return Response({
        'success': True,
        'staff': serializer.data,
        'pagination': {
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def staff_stats_view(request):
    """
    Get staff statistics
    GET /api/auth/staff/stats/
    """
    # Check if user is admin
    if request.user.role != 'admin' and not request.user.is_superuser:
        return Response({
            'success': False,
            'message': 'Permission denied. Admin access required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    stats = {
        'total_staff': User.objects.count(),
        'by_role': {}
    }
    
    for role_code, role_name in User.ROLE_CHOICES:
        stats['by_role'][role_code] = {
            'name': role_name,
            'count': User.objects.filter(role=role_code).count()
        }
    
    stats['active_staff'] = User.objects.filter(is_active=True).count()
    stats['inactive_staff'] = User.objects.filter(is_active=False).count()
    
    return Response({
        'success': True,
        'stats': stats
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def staff_detail_view(request, pk):
    """
    Get staff member details
    GET /api/auth/staff/<id>/
    """
    # Check if user is admin
    if request.user.role != 'admin' and not request.user.is_superuser:
        return Response({
            'success': False,
            'message': 'Permission denied. Admin access required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        staff_member = User.objects.get(pk=pk)
        serializer = UserSerializer(staff_member)
        return Response({
            'success': True,
            'staff': serializer.data
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Staff member not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def staff_update_view(request, pk):
    """
    Update staff member
    PUT/PATCH /api/auth/staff/<id>/update/
    """
    # Check if user is admin
    if request.user.role != 'admin' and not request.user.is_superuser:
        return Response({
            'success': False,
            'message': 'Permission denied. Admin access required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        staff_member = User.objects.get(pk=pk)
        serializer = UserSerializer(staff_member, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Staff member updated successfully',
                'staff': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Staff member not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def staff_delete_view(request, pk):
    """
    Delete staff member
    DELETE /api/auth/staff/<id>/
    """
    # Check if user is admin
    if request.user.role != 'admin' and not request.user.is_superuser:
        return Response({
            'success': False,
            'message': 'Permission denied. Admin access required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        staff_member = User.objects.get(pk=pk)
        
        # Prevent deleting yourself
        if staff_member.id == request.user.id:
            return Response({
                'success': False,
                'message': 'You cannot delete your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        staff_member.delete()
        return Response({
            'success': True,
            'message': 'Staff member deleted successfully'
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Staff member not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def staff_create_view(request):
    """
    Create new staff member (Admin only)
    POST /api/auth/staff/create/
    Body: {
        "username": "...",
        "email": "...",
        "password": "...",
        "password_confirm": "...",
        "first_name": "...",
        "last_name": "...",
        "role": "doctor|nurse|admin|...",
        "phone_number": "..."
    }
    """
    # Check if user is admin
    if request.user.role != 'admin' and not request.user.is_superuser:
        return Response({
            'success': False,
            'message': 'Permission denied. Admin access required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'success': True,
            'message': 'Staff member created successfully',
            'staff': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    
    # Return detailed error messages
    error_messages = []
    for field, errors in serializer.errors.items():
        if isinstance(errors, list):
            error_messages.extend([f"{field}: {error}" for error in errors])
        else:
            error_messages.append(f"{field}: {errors}")
    
    return Response({
        'success': False,
        'message': 'Failed to create staff member',
        'errors': serializer.errors,
        'error': '; '.join(error_messages) if error_messages else 'Invalid data'
    }, status=status.HTTP_400_BAD_REQUEST)
