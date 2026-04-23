from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import VitalSign, MedicationRecord
from .serializers import VitalSignSerializer, MedicationRecordSerializer


# ─── Vital Signs ──────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vital_sign_list_view(request):
    vitals = VitalSign.objects.select_related('patient', 'recorded_by').all()

    patient_id = request.query_params.get('patient_id')
    if patient_id:
        vitals = vitals.filter(patient_id=patient_id)

    date = request.query_params.get('date')
    if date:
        vitals = vitals.filter(recorded_at__date=date)

    page_number = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page_number - 1) * page_size
    end = start + page_size
    total = vitals.count()

    serializer = VitalSignSerializer(vitals[start:end], many=True)
    return Response({
        'success': True,
        'vital_signs': serializer.data,
        'pagination': {
            'total': total,
            'page': page_number,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vital_sign_create_view(request):
    serializer = VitalSignSerializer(data=request.data)
    if serializer.is_valid():
        vital = serializer.save(recorded_by=request.user)
        return Response({
            'success': True,
            'message': 'Vital signs recorded successfully',
            'vital_sign': VitalSignSerializer(vital).data
        }, status=status.HTTP_201_CREATED)
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vital_sign_detail_view(request, pk):
    try:
        vital = VitalSign.objects.get(pk=pk)
        return Response({'success': True, 'vital_sign': VitalSignSerializer(vital).data})
    except VitalSign.DoesNotExist:
        return Response({'success': False, 'message': 'Vital sign record not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vital_sign_stats_view(request):
    from django.db.models import Avg

    vitals = VitalSign.objects.all()
    patient_id = request.query_params.get('patient_id')
    if patient_id:
        vitals = vitals.filter(patient_id=patient_id)

    recent_cutoff = timezone.now() - timezone.timedelta(days=7)
    stats = vitals.aggregate(
        avg_temp=Avg('temperature'),
        avg_systolic=Avg('blood_pressure_systolic'),
        avg_diastolic=Avg('blood_pressure_diastolic'),
        avg_heart_rate=Avg('heart_rate'),
        avg_o2=Avg('oxygen_saturation'),
    )

    return Response({
        'success': True,
        'stats': {
            'total_records': vitals.count(),
            'recent_records': vitals.filter(recorded_at__gte=recent_cutoff).count(),
            'average_temperature': round(float(stats['avg_temp']), 1) if stats['avg_temp'] else None,
            'average_blood_pressure_systolic': round(float(stats['avg_systolic']), 0) if stats['avg_systolic'] else None,
            'average_blood_pressure_diastolic': round(float(stats['avg_diastolic']), 0) if stats['avg_diastolic'] else None,
            'average_heart_rate': round(float(stats['avg_heart_rate']), 0) if stats['avg_heart_rate'] else None,
            'average_oxygen_saturation': round(float(stats['avg_o2']), 1) if stats['avg_o2'] else None,
        }
    })


# ─── Medication Records ────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def medication_list_view(request):
    medications = MedicationRecord.objects.select_related('patient', 'administered_by').all()

    patient_id = request.query_params.get('patient_id')
    if patient_id:
        medications = medications.filter(patient_id=patient_id)

    status_filter = request.query_params.get('status')
    if status_filter:
        medications = medications.filter(status=status_filter)

    page_number = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page_number - 1) * page_size
    end = start + page_size
    total = medications.count()

    serializer = MedicationRecordSerializer(medications[start:end], many=True)
    return Response({
        'success': True,
        'medications': serializer.data,
        'pagination': {
            'total': total,
            'page': page_number,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def medication_create_view(request):
    serializer = MedicationRecordSerializer(data=request.data)
    if serializer.is_valid():
        medication = serializer.save()
        return Response({
            'success': True,
            'message': 'Medication recorded successfully',
            'medication': MedicationRecordSerializer(medication).data
        }, status=status.HTTP_201_CREATED)
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def medication_detail_view(request, pk):
    try:
        medication = MedicationRecord.objects.get(pk=pk)
        return Response({'success': True, 'medication': MedicationRecordSerializer(medication).data})
    except MedicationRecord.DoesNotExist:
        return Response({'success': False, 'message': 'Medication record not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def medication_update_view(request, pk):
    try:
        medication = MedicationRecord.objects.get(pk=pk)
    except MedicationRecord.DoesNotExist:
        return Response({'success': False, 'message': 'Medication record not found'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if new_status == 'administered' and medication.status != 'administered':
        medication.administered_by = request.user
        medication.administered_at = timezone.now()
        medication.save(update_fields=['administered_by', 'administered_at'])

    serializer = MedicationRecordSerializer(medication, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Medication record updated successfully',
            'medication': serializer.data
        })
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def medication_delete_view(request, pk):
    try:
        MedicationRecord.objects.get(pk=pk).delete()
        return Response({'success': True, 'message': 'Medication record deleted'})
    except MedicationRecord.DoesNotExist:
        return Response({'success': False, 'message': 'Medication record not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def medication_stats_view(request):
    medications = MedicationRecord.objects.all()
    patient_id = request.query_params.get('patient_id')
    if patient_id:
        medications = medications.filter(patient_id=patient_id)

    today = timezone.now().date()
    by_status = {}
    for key, label in MedicationRecord.STATUS_CHOICES:
        count = medications.filter(status=key).count()
        by_status[key] = {'name': label, 'count': count}

    return Response({
        'success': True,
        'stats': {
            'total_records': medications.count(),
            'today_records': medications.filter(created_at__date=today).count(),
            'pending': medications.filter(status='pending').count(),
            'administered': medications.filter(status='administered').count(),
            'missed': medications.filter(status='missed').count(),
            'cancelled': medications.filter(status='cancelled').count(),
            'by_status': by_status,
        }
    })
