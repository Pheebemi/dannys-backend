from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.db import IntegrityError
from .models import Patient, HMO
from .serializers import PatientSerializer, PatientCreateSerializer, HMOSerializer


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

    # Patients can only see their own record
    if request.user.role == 'patient':
        patients = patients.filter(user=request.user)

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
    Create a new patient + a portal User account in one step.
    Default password = patient's phone number.
    POST /api/patients/create/
    """
    from django.db import transaction
    from django.contrib.auth import get_user_model
    User = get_user_model()

    serializer = PatientCreateSerializer(data=request.data)

    if not serializer.is_valid():
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

    try:
        from django.db.models.signals import post_save
        from patients.signals import create_patient_record_for_patient_user

        with transaction.atomic():
            data = serializer.validated_data
            email = data.get('email')
            phone = data.get('phone_number', '')
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')

            default_password = phone

            portal_user = None
            if email:
                if User.objects.filter(email=email).exists():
                    return Response({
                        'success': False,
                        'message': 'A user account with this email already exists.',
                        'errors': {'email': ['A user account with this email already exists.']}
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Disconnect signal so it doesn't auto-create a Patient —
                # we create the Patient ourselves below with full details
                post_save.disconnect(create_patient_record_for_patient_user, sender=User)
                try:
                    portal_user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=default_password,
                        first_name=first_name,
                        last_name=last_name,
                        role='patient',
                        phone_number=phone,
                    )
                finally:
                    post_save.connect(create_patient_record_for_patient_user, sender=User)

            # Create Patient record with full details linked to the user
            patient = serializer.save(
                created_by=request.user,
                user=portal_user,
            )

        response_data = {
            'success': True,
            'message': 'Patient and portal account created successfully',
            'patient': PatientSerializer(patient).data,
        }
        if portal_user and email:
            response_data['portal_credentials'] = {
                'email': email,
                'default_password': default_password,
                'note': "Share these credentials with the patient. They can log in at /patient/login and should change their password."
            }
        else:
            response_data['message'] = 'Patient created. No portal account was created (no email provided).'

        return Response(response_data, status=status.HTTP_201_CREATED)

    except IntegrityError as e:
        err = str(e).lower()
        if 'email' in err:
            return Response({
                'success': False,
                'message': 'A patient with this email already exists.',
                'errors': {'email': ['A patient with this email already exists.']}
            }, status=status.HTTP_400_BAD_REQUEST)
        if 'phone' in err:
            return Response({
                'success': False,
                'message': 'A patient with this phone number already exists.',
                'errors': {'phone_number': ['This phone number is already registered.']}
            }, status=status.HTTP_400_BAD_REQUEST)
        if 'patient_code' in err:
            return Response({
                'success': False,
                'message': 'A patient ID conflict occurred. Please try again.',
            }, status=status.HTTP_400_BAD_REQUEST)
        if 'username' in err:
            return Response({
                'success': False,
                'message': 'A user account with this email already exists.',
                'errors': {'email': ['A portal account with this email already exists.']}
            }, status=status.HTTP_400_BAD_REQUEST)
        # Log the actual error for debugging and return it
        import logging
        logging.getLogger(__name__).error(f"Patient create IntegrityError: {e}")
        return Response({
            'success': False,
            'message': f'Data conflict: {str(e)}',
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



# ─── HMO Views ────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hmo_list_view(request):
    from django.db.models import Count
    hmos = HMO.objects.annotate(patient_count=Count('patients')).order_by('name')
    data = HMOSerializer(hmos, many=True).data
    # Attach patient_count to each item
    for item, hmo in zip(data, hmos):
        item['patient_count'] = hmo.patient_count
    return Response({'success': True, 'hmos': data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def hmo_create_view(request):
    if request.user.role not in ['admin'] and not request.user.is_superuser:
        return Response({'success': False, 'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    serializer = HMOSerializer(data=request.data)
    if serializer.is_valid():
        hmo = serializer.save()
        return Response({'success': True, 'message': 'HMO created', 'hmo': HMOSerializer(hmo).data}, status=status.HTTP_201_CREATED)
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def hmo_update_view(request, pk):
    if request.user.role not in ['admin'] and not request.user.is_superuser:
        return Response({'success': False, 'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    try:
        hmo = HMO.objects.get(pk=pk)
    except HMO.DoesNotExist:
        return Response({'success': False, 'message': 'HMO not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = HMOSerializer(hmo, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'message': 'HMO updated', 'hmo': serializer.data})
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def hmo_delete_view(request, pk):
    if request.user.role not in ['admin'] and not request.user.is_superuser:
        return Response({'success': False, 'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    try:
        HMO.objects.get(pk=pk).delete()
        return Response({'success': True, 'message': 'HMO deleted'})
    except HMO.DoesNotExist:
        return Response({'success': False, 'message': 'HMO not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_portal_status_view(request, pk):
    """Check if a patient has a portal account linked."""
    try:
        patient = Patient.objects.get(pk=pk)
        return Response({
            'success': True,
            'has_portal_account': patient.user is not None,
            'portal_email': patient.user.email if patient.user else None,
        })
    except Patient.DoesNotExist:
        return Response({'success': False, 'message': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
