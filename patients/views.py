from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import Patient
from .serializers import PatientSerializer, PatientCreateSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_list_view(request):
    """
    List all patients with filtering and search
    GET /api/patients/
    Query Params:
        search (str): Search by name, email, phone
        gender (str): Filter by gender
        is_active (bool): Filter by active status
        assigned_doctor_id (int): Filter by assigned doctor
        my_patients (bool): If true and user is doctor, show only their assigned patients
        page (int): Page number
        page_size (int): Number of items per page
    """
    patients = Patient.objects.all().order_by('-created_at')
    
    # If user is a doctor and my_patients is true, filter by assigned doctor
    if request.user.role == 'doctor' and request.query_params.get('my_patients', '').lower() == 'true':
        patients = patients.filter(assigned_doctor=request.user)
    # If assigned_doctor_id is provided, filter by that doctor
    elif request.query_params.get('assigned_doctor_id'):
        patients = patients.filter(assigned_doctor_id=request.query_params.get('assigned_doctor_id'))
    
    # Search filter
    search_query = request.query_params.get('search')
    if search_query:
        patients = patients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    # Gender filter
    gender = request.query_params.get('gender')
    if gender:
        patients = patients.filter(gender=gender)
    
    # Active status filter
    is_active = request.query_params.get('is_active')
    if is_active is not None:
        is_active_bool = is_active.lower() == 'true'
        patients = patients.filter(is_active=is_active_bool)
    
    # Pagination
    page_number = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    
    total_patients = patients.count()
    paginated_patients = patients[start_index:end_index]
    
    serializer = PatientSerializer(paginated_patients, many=True)
    return Response({
        'success': True,
        'patients': serializer.data,
        'pagination': {
            'total': total_patients,
            'page': page_number,
            'page_size': page_size,
            'total_pages': (total_patients + page_size - 1) // page_size,
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def patient_create_view(request):
    """
    Create a new patient
    POST /api/patients/create/
    """
    serializer = PatientCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        patient = serializer.save(created_by=request.user)
        return Response({
            'success': True,
            'message': 'Patient created successfully',
            'patient': PatientSerializer(patient).data
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
        'message': 'Failed to create patient',
        'errors': serializer.errors,
        'error': '; '.join(error_messages) if error_messages else 'Invalid data'
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_detail_view(request, pk):
    """
    Get patient details
    GET /api/patients/<id>/
    """
    try:
        patient = Patient.objects.get(pk=pk)
        serializer = PatientSerializer(patient)
        return Response({
            'success': True,
            'patient': serializer.data
        }, status=status.HTTP_200_OK)
    except Patient.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Patient not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def patient_update_view(request, pk):
    """
    Update patient
    PUT/PATCH /api/patients/<id>/update/
    """
    try:
        patient = Patient.objects.get(pk=pk)
        serializer = PatientSerializer(patient, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Patient updated successfully',
                'patient': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except Patient.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Patient not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def patient_delete_view(request, pk):
    """
    Delete patient
    DELETE /api/patients/<id>/delete/
    """
    try:
        patient = Patient.objects.get(pk=pk)
        patient.delete()
        return Response({
            'success': True,
            'message': 'Patient deleted successfully'
        }, status=status.HTTP_200_OK)
    except Patient.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Patient not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_stats_view(request):
    """
    Get patient statistics
    GET /api/patients/stats/
    """
    from django.db.models import Count
    
    total_patients = Patient.objects.count()
    active_patients = Patient.objects.filter(is_active=True).count()
    inactive_patients = Patient.objects.filter(is_active=False).count()
    
    patients_by_gender = Patient.objects.values('gender').annotate(count=Count('gender'))
    gender_stats = {}
    for item in patients_by_gender:
        gender_stats[item['gender']] = {
            'name': dict(Patient.GENDER_CHOICES).get(item['gender'], item['gender']),
            'count': item['count']
        }
    
    return Response({
        'success': True,
        'stats': {
            'total_patients': total_patients,
            'active_patients': active_patients,
            'inactive_patients': inactive_patients,
            'by_gender': gender_stats,
        }
    }, status=status.HTTP_200_OK)

