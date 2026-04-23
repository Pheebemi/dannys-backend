from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import Prescription, PrescriptionItem, MedicationInventory
from .serializers import (
    PrescriptionSerializer, PrescriptionCreateSerializer,
    PrescriptionItemSerializer, MedicationInventorySerializer,
)

PHARMACY_ROLES = ['pharmacist', 'admin']


def is_pharmacy_staff(user):
    return user.role in PHARMACY_ROLES or user.is_superuser


# ─── Prescriptions ────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prescription_list_view(request):
    prescriptions = Prescription.objects.select_related(
        'patient', 'prescribed_by', 'dispensed_by'
    ).prefetch_related('items').all()

    status_filter = request.query_params.get('status')
    if status_filter:
        prescriptions = prescriptions.filter(status=status_filter)

    patient_id = request.query_params.get('patient_id')
    if patient_id:
        prescriptions = prescriptions.filter(patient_id=patient_id)

    search = request.query_params.get('search')
    if search:
        from django.db.models import Q
        prescriptions = prescriptions.filter(
            Q(patient__first_name__icontains=search) |
            Q(patient__last_name__icontains=search) |
            Q(items__medication_name__icontains=search)
        ).distinct()

    page_number = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page_number - 1) * page_size
    end = start + page_size

    total = prescriptions.count()
    serializer = PrescriptionSerializer(prescriptions[start:end], many=True)

    return Response({
        'success': True,
        'prescriptions': serializer.data,
        'pagination': {
            'total': total,
            'page': page_number,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def prescription_create_view(request):
    serializer = PrescriptionCreateSerializer(data=request.data)
    if serializer.is_valid():
        prescription = serializer.save()
        return Response({
            'success': True,
            'message': 'Prescription sent to pharmacy',
            'prescription': PrescriptionSerializer(prescription).data
        }, status=status.HTTP_201_CREATED)
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prescription_detail_view(request, pk):
    try:
        prescription = Prescription.objects.prefetch_related('items').get(pk=pk)
        return Response({'success': True, 'prescription': PrescriptionSerializer(prescription).data})
    except Prescription.DoesNotExist:
        return Response({'success': False, 'message': 'Prescription not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def prescription_update_view(request, pk):
    try:
        prescription = Prescription.objects.get(pk=pk)
    except Prescription.DoesNotExist:
        return Response({'success': False, 'message': 'Prescription not found'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if new_status == 'dispensed' and prescription.status != 'dispensed':
        prescription.dispensed_by = request.user
        prescription.dispensed_at = timezone.now()
        prescription.save(update_fields=['dispensed_by', 'dispensed_at'])

    serializer = PrescriptionSerializer(prescription, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Prescription updated successfully',
            'prescription': PrescriptionSerializer(prescription).data
        })
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def prescription_delete_view(request, pk):
    try:
        Prescription.objects.get(pk=pk).delete()
        return Response({'success': True, 'message': 'Prescription deleted successfully'})
    except Prescription.DoesNotExist:
        return Response({'success': False, 'message': 'Prescription not found'}, status=status.HTTP_404_NOT_FOUND)


# ─── Inventory ────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_list_view(request):
    items = MedicationInventory.objects.filter(is_active=True)

    search = request.query_params.get('search')
    if search:
        from django.db.models import Q
        items = items.filter(
            Q(medication_name__icontains=search) |
            Q(generic_name__icontains=search) |
            Q(category__icontains=search)
        )

    low_stock = request.query_params.get('low_stock')
    if low_stock == 'true':
        from django.db.models import F
        items = items.filter(stock_quantity__lte=F('reorder_level'))

    category = request.query_params.get('category')
    if category:
        items = items.filter(category__iexact=category)

    page_number = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page_number - 1) * page_size
    end = start + page_size

    total = items.count()
    serializer = MedicationInventorySerializer(items[start:end], many=True)

    return Response({
        'success': True,
        'items': serializer.data,
        'pagination': {
            'total': total,
            'page': page_number,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def inventory_create_view(request):
    if not is_pharmacy_staff(request.user):
        return Response({'success': False, 'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    serializer = MedicationInventorySerializer(data=request.data)
    if serializer.is_valid():
        item = serializer.save()
        return Response({
            'success': True,
            'message': 'Medication added to inventory',
            'item': MedicationInventorySerializer(item).data
        }, status=status.HTTP_201_CREATED)
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_detail_view(request, pk):
    try:
        item = MedicationInventory.objects.get(pk=pk)
        return Response({'success': True, 'item': MedicationInventorySerializer(item).data})
    except MedicationInventory.DoesNotExist:
        return Response({'success': False, 'message': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def inventory_update_view(request, pk):
    if not is_pharmacy_staff(request.user):
        return Response({'success': False, 'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    try:
        item = MedicationInventory.objects.get(pk=pk)
    except MedicationInventory.DoesNotExist:
        return Response({'success': False, 'message': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = MedicationInventorySerializer(item, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'message': 'Inventory updated successfully', 'item': serializer.data})
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def inventory_delete_view(request, pk):
    if not is_pharmacy_staff(request.user):
        return Response({'success': False, 'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    try:
        MedicationInventory.objects.get(pk=pk).delete()
        return Response({'success': True, 'message': 'Item deleted successfully'})
    except MedicationInventory.DoesNotExist:
        return Response({'success': False, 'message': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)


# ─── Stats ────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pharmacy_stats_view(request):
    from django.db.models import F

    pending = Prescription.objects.filter(status='pending').count()
    ready = Prescription.objects.filter(status='ready').count()
    dispensed_today = Prescription.objects.filter(
        status='dispensed',
        dispensed_at__date=timezone.now().date()
    ).count()

    total_inventory = MedicationInventory.objects.filter(is_active=True).count()
    low_stock_count = MedicationInventory.objects.filter(
        is_active=True, stock_quantity__lte=F('reorder_level')
    ).count()

    return Response({
        'success': True,
        'stats': {
            'pending_prescriptions': pending,
            'ready_for_pickup': ready,
            'dispensed_today': dispensed_today,
            'total_inventory': total_inventory,
            'low_stock_items': low_stock_count,
        }
    })
