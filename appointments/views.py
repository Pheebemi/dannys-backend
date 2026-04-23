from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models import Appointment
from .serializers import AppointmentSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_list_view(request):
    appointments = Appointment.objects.select_related(
        'patient', 'doctor', 'checked_in_by', 'created_by'
    ).all()

    # Doctors only see their own appointments
    if request.user.role == 'doctor':
        appointments = appointments.filter(doctor=request.user)

    date = request.query_params.get('date')
    if date:
        appointments = appointments.filter(appointment_date=date)

    start_date = request.query_params.get('start_date')
    if start_date:
        appointments = appointments.filter(appointment_date__gte=start_date)

    end_date = request.query_params.get('end_date')
    if end_date:
        appointments = appointments.filter(appointment_date__lte=end_date)

    status_filter = request.query_params.get('status')
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    doctor_id = request.query_params.get('doctor_id')
    if doctor_id:
        appointments = appointments.filter(doctor_id=doctor_id)

    patient_id = request.query_params.get('patient_id')
    if patient_id:
        appointments = appointments.filter(patient_id=patient_id)

    search = request.query_params.get('search')
    if search:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=search) |
            Q(patient__last_name__icontains=search) |
            Q(doctor__first_name__icontains=search) |
            Q(doctor__last_name__icontains=search)
        )

    serializer = AppointmentSerializer(appointments, many=True)
    return Response({
        'success': True,
        'count': appointments.count(),
        'appointments': serializer.data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def appointment_create_view(request):
    serializer = AppointmentSerializer(data=request.data)
    if serializer.is_valid():
        appointment = serializer.save(created_by=request.user)
        return Response({
            'success': True,
            'message': 'Appointment created successfully',
            'appointment': AppointmentSerializer(appointment).data
        }, status=status.HTTP_201_CREATED)
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_detail_view(request, pk):
    try:
        appointment = Appointment.objects.get(pk=pk)
        return Response({'success': True, 'appointment': AppointmentSerializer(appointment).data})
    except Appointment.DoesNotExist:
        return Response({'success': False, 'message': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def appointment_update_view(request, pk):
    try:
        appointment = Appointment.objects.get(pk=pk)
    except Appointment.DoesNotExist:
        return Response({'success': False, 'message': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if new_status == 'completed' and appointment.status != 'completed':
        appointment.completed_at = timezone.now()
        appointment.save(update_fields=['completed_at'])

    serializer = AppointmentSerializer(appointment, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Appointment updated successfully',
            'appointment': AppointmentSerializer(appointment).data
        })
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def appointment_delete_view(request, pk):
    try:
        Appointment.objects.get(pk=pk).delete()
        return Response({'success': True, 'message': 'Appointment deleted successfully'})
    except Appointment.DoesNotExist:
        return Response({'success': False, 'message': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def appointment_checkin_view(request, pk):
    try:
        appointment = Appointment.objects.get(pk=pk)
    except Appointment.DoesNotExist:
        return Response({'success': False, 'message': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

    if appointment.status not in ['scheduled']:
        return Response({
            'success': False,
            'message': f'Cannot check in — appointment is already {appointment.get_status_display()}'
        }, status=status.HTTP_400_BAD_REQUEST)

    appointment.status = 'checked_in'
    appointment.checked_in_at = timezone.now()
    appointment.checked_in_by = request.user
    appointment.save(update_fields=['status', 'checked_in_at', 'checked_in_by'])

    return Response({
        'success': True,
        'message': 'Patient checked in successfully',
        'appointment': AppointmentSerializer(appointment).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_stats_view(request):
    today = timezone.now().date()
    today_qs = Appointment.objects.filter(appointment_date=today)

    if request.user.role == 'doctor':
        today_qs = today_qs.filter(doctor=request.user)

    from django.db.models import Count
    status_breakdown = {
        item['status']: item['count']
        for item in Appointment.objects.values('status').annotate(count=Count('status'))
    }

    return Response({
        'success': True,
        'stats': {
            'today': {
                'total': today_qs.count(),
                'checked_in': today_qs.filter(status='checked_in').count(),
                'waiting': today_qs.filter(status='scheduled').count(),
                'completed': today_qs.filter(status='completed').count(),
                'pending': today_qs.filter(status='scheduled').count(),
            },
            'this_week': {
                'total': Appointment.objects.filter(
                    appointment_date__gte=today,
                    appointment_date__lte=today + timezone.timedelta(days=7)
                ).count()
            },
            'status_breakdown': status_breakdown,
        }
    })
