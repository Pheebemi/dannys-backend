from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import RadiologyCategory, RadiologyTest, RadiologyResult
from .serializers import (
    RadiologyCategorySerializer,
    RadiologyTestSerializer,
    RadiologyTestCreateSerializer,
    RadiologyTestUpdateSerializer,
    RadiologyResultSerializer,
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def radiology_test_list_view(request):
    tests = RadiologyTest.objects.select_related('patient', 'category', 'ordered_by', 'performed_by').all()

    if request.user.role == 'patient':
        try:
            tests = tests.filter(patient=request.user.patient_profile)
        except Exception:
            return Response({'success': True, 'tests': [], 'pagination': {'total': 0, 'page': 1, 'page_size': 20, 'total_pages': 0}})

    status_filter = request.query_params.get('status')
    if status_filter:
        tests = tests.filter(status=status_filter)

    priority_filter = request.query_params.get('priority')
    if priority_filter:
        tests = tests.filter(priority=priority_filter)

    patient_id = request.query_params.get('patient_id')
    if patient_id:
        tests = tests.filter(patient_id=patient_id)

    search = request.query_params.get('search')
    if search:
        from django.db.models import Q
        tests = tests.filter(
            Q(test_name__icontains=search) |
            Q(patient__first_name__icontains=search) |
            Q(patient__last_name__icontains=search)
        )

    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    total = tests.count()

    serializer = RadiologyTestSerializer(tests[start:end], many=True)
    return Response({
        'success': True,
        'tests': serializer.data,
        'pagination': {
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': max(1, -(-total // page_size)),
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def radiology_test_create_view(request):
    serializer = RadiologyTestCreateSerializer(data=request.data)
    if serializer.is_valid():
        test = serializer.save(ordered_by=request.user)
        return Response({
            'success': True,
            'message': 'Radiology test ordered successfully',
            'test': RadiologyTestSerializer(test).data,
        }, status=status.HTTP_201_CREATED)
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def radiology_test_detail_view(request, pk):
    try:
        test = RadiologyTest.objects.select_related('patient', 'category', 'ordered_by', 'performed_by').get(pk=pk)
        return Response({'success': True, 'test': RadiologyTestSerializer(test).data})
    except RadiologyTest.DoesNotExist:
        return Response({'success': False, 'message': 'Radiology test not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def radiology_test_update_view(request, pk):
    try:
        test = RadiologyTest.objects.get(pk=pk)
    except RadiologyTest.DoesNotExist:
        return Response({'success': False, 'message': 'Radiology test not found'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if new_status == 'in_progress' and not test.performed_by:
        test.performed_by = request.user
        test.save(update_fields=['performed_by'])
    if new_status == 'completed' and not test.completed_date:
        test.completed_date = timezone.now()
        test.save(update_fields=['completed_date'])

    serializer = RadiologyTestUpdateSerializer(test, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'message': 'Updated successfully', 'test': RadiologyTestSerializer(test).data})
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def radiology_test_delete_view(request, pk):
    try:
        RadiologyTest.objects.get(pk=pk).delete()
        return Response({'success': True, 'message': 'Radiology test deleted'})
    except RadiologyTest.DoesNotExist:
        return Response({'success': False, 'message': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def radiology_result_create_view(request, test_id):
    try:
        test = RadiologyTest.objects.get(pk=test_id)
    except RadiologyTest.DoesNotExist:
        return Response({'success': False, 'message': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)

    data = {**request.data, 'test': test.id}
    serializer = RadiologyResultSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'result': serializer.data}, status=status.HTTP_201_CREATED)
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def radiology_result_detail_view(request, test_id, result_id):
    try:
        result = RadiologyResult.objects.get(pk=result_id, test_id=test_id)
    except RadiologyResult.DoesNotExist:
        return Response({'success': False, 'message': 'Result not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        result.delete()
        return Response({'success': True, 'message': 'Result deleted'})

    serializer = RadiologyResultSerializer(result, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'result': serializer.data})
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def radiology_category_list_view(request):
    if request.method == 'GET':
        categories = RadiologyCategory.objects.all()
        return Response({'success': True, 'categories': RadiologyCategorySerializer(categories, many=True).data})

    if request.user.role not in ['admin', 'radiologist'] and not request.user.is_superuser:
        return Response({'success': False, 'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    serializer = RadiologyCategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'category': serializer.data}, status=status.HTTP_201_CREATED)
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def radiology_stats_view(request):
    if request.user.role not in ['admin', 'radiologist'] and not request.user.is_superuser:
        return Response({'success': False, 'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    total = RadiologyTest.objects.count()
    pending = RadiologyTest.objects.filter(status='pending').count()
    in_progress = RadiologyTest.objects.filter(status='in_progress').count()
    completed = RadiologyTest.objects.filter(status='completed').count()
    return Response({
        'success': True,
        'stats': {
            'total_tests': total,
            'pending_tests': pending,
            'in_progress_tests': in_progress,
            'completed_tests': completed,
        }
    })
