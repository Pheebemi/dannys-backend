from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from patients.models import Patient

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_overview_view(request):
    """
    Get analytics overview with key metrics
    GET /api/reports/analytics/
    Query Params:
        start_date (YYYY-MM-DD): Start date for date range
        end_date (YYYY-MM-DD): End date for date range
    """
    # Check if user is admin
    if request.user.role != 'admin' and not request.user.is_superuser:
        return Response({
            'success': False,
            'message': 'Permission denied. Admin access required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Get date range from query params
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    # Default to last 30 days if not provided
    if not end_date:
        end_date = timezone.now().date()
    else:
        from datetime import datetime
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    if not start_date:
        start_date = end_date - timedelta(days=30)
    else:
        from datetime import datetime
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    # Staff Statistics
    total_staff = User.objects.count()
    active_staff = User.objects.filter(is_active=True).count()
    staff_by_role = {}
    for role_code, role_name in User.ROLE_CHOICES:
        staff_by_role[role_code] = {
            'name': role_name,
            'count': User.objects.filter(role=role_code).count()
        }
    
    # Patient Statistics
    total_patients = Patient.objects.count()
    active_patients = Patient.objects.filter(is_active=True).count()
    new_patients = Patient.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).count()
    
    patients_by_gender = Patient.objects.values('gender').annotate(count=Count('gender'))
    gender_stats = {}
    for item in patients_by_gender:
        gender_stats[item['gender']] = {
            'name': dict(Patient.GENDER_CHOICES).get(item['gender'], item['gender']),
            'count': item['count']
        }
    
    # Patient registration trend (last 7 days)
    patient_trend = []
    for i in range(6, -1, -1):
        date = end_date - timedelta(days=i)
        count = Patient.objects.filter(created_at__date=date).count()
        patient_trend.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Staff registration trend (last 7 days)
    staff_trend = []
    for i in range(6, -1, -1):
        date = end_date - timedelta(days=i)
        count = User.objects.filter(created_at__date=date).count()
        staff_trend.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Age distribution
    age_groups = {
        '0-18': Patient.objects.filter(date_of_birth__gte=timezone.now().date() - timedelta(days=18*365)).count(),
        '19-35': Patient.objects.filter(
            date_of_birth__gte=timezone.now().date() - timedelta(days=35*365),
            date_of_birth__lt=timezone.now().date() - timedelta(days=18*365)
        ).count(),
        '36-50': Patient.objects.filter(
            date_of_birth__gte=timezone.now().date() - timedelta(days=50*365),
            date_of_birth__lt=timezone.now().date() - timedelta(days=35*365)
        ).count(),
        '51-65': Patient.objects.filter(
            date_of_birth__gte=timezone.now().date() - timedelta(days=65*365),
            date_of_birth__lt=timezone.now().date() - timedelta(days=50*365)
        ).count(),
        '65+': Patient.objects.filter(
            date_of_birth__lt=timezone.now().date() - timedelta(days=65*365)
        ).count(),
    }
    
    return Response({
        'success': True,
        'analytics': {
            'date_range': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
            },
            'staff': {
                'total': total_staff,
                'active': active_staff,
                'inactive': total_staff - active_staff,
                'by_role': staff_by_role,
            },
            'patients': {
                'total': total_patients,
                'active': active_patients,
                'inactive': total_patients - active_patients,
                'new_in_period': new_patients,
                'by_gender': gender_stats,
                'age_distribution': age_groups,
            },
            'trends': {
                'patient_registrations': patient_trend,
                'staff_registrations': staff_trend,
            },
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def staff_report_view(request):
    """
    Get detailed staff report
    GET /api/reports/staff/
    """
    if request.user.role != 'admin' and not request.user.is_superuser:
        return Response({
            'success': False,
            'message': 'Permission denied. Admin access required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    staff = User.objects.all().order_by('-created_at')
    staff_data = []
    
    for member in staff:
        staff_data.append({
            'id': member.id,
            'name': member.full_name,
            'username': member.username,
            'email': member.email,
            'role': member.get_role_display(),
            'role_code': member.role,
            'is_active': member.is_active,
            'date_joined': member.created_at.strftime('%Y-%m-%d') if member.created_at else 'N/A',
            'last_login': member.last_login.strftime('%Y-%m-%d %H:%M:%S') if member.last_login else None,
        })
    
    return Response({
        'success': True,
        'report': {
            'type': 'staff',
            'total': len(staff_data),
            'data': staff_data,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_report_view(request):
    """
    Get detailed patient report
    GET /api/reports/patients/
    Query Params:
        start_date (YYYY-MM-DD): Start date for date range
        end_date (YYYY-MM-DD): End date for date range
    """
    if request.user.role != 'admin' and not request.user.is_superuser:
        return Response({
            'success': False,
            'message': 'Permission denied. Admin access required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    patients = Patient.objects.all().order_by('-created_at')
    
    if start_date:
        from datetime import datetime
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        patients = patients.filter(created_at__date__gte=start_date)
    
    if end_date:
        from datetime import datetime
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        patients = patients.filter(created_at__date__lte=end_date)
    
    patient_data = []
    for patient in patients:
        patient_data.append({
            'id': patient.id,
            'name': patient.full_name,
            'email': patient.email,
            'phone': patient.phone_number,
            'gender': patient.get_gender_display(),
            'age': patient.age,
            'blood_type': patient.blood_type or 'Unknown',
            'is_active': patient.is_active,
            'created_at': patient.created_at.strftime('%Y-%m-%d'),
        })
    
    return Response({
        'success': True,
        'report': {
            'type': 'patients',
            'total': len(patient_data),
            'data': patient_data,
        }
    }, status=status.HTTP_200_OK)

