from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import LabTest, LabTestCategory, LabTestResult
from .serializers import (
    LabTestSerializer, LabTestCreateSerializer, LabTestCategorySerializer,
    LabTestResultSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lab_test_list_view(request):
    """
    List all lab tests with filtering
    GET /api/lab-tests/
    Query Params:
        status (str): Filter by status
        patient_id (int): Filter by patient
        category_id (int): Filter by category
        priority (str): Filter by priority
        page (int): Page number
        page_size (int): Items per page
    """
    tests = LabTest.objects.all().order_by('-ordered_date', '-created_at')
    
    # Filters
    status_filter = request.query_params.get('status')
    if status_filter:
        tests = tests.filter(status=status_filter)
    
    patient_id = request.query_params.get('patient_id')
    if patient_id:
        tests = tests.filter(patient_id=patient_id)
    
    category_id = request.query_params.get('category_id')
    if category_id:
        tests = tests.filter(category_id=category_id)
    
    priority = request.query_params.get('priority')
    if priority:
        tests = tests.filter(priority=priority)
    
    # Pagination
    page_number = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    
    total_tests = tests.count()
    paginated_tests = tests[start_index:end_index]
    
    serializer = LabTestSerializer(paginated_tests, many=True)
    return Response({
        'success': True,
        'tests': serializer.data,
        'pagination': {
            'total': total_tests,
            'page': page_number,
            'page_size': page_size,
            'total_pages': (total_tests + page_size - 1) // page_size,
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def lab_test_create_view(request):
    """
    Create a new lab test
    POST /api/lab-tests/create/
    """
    serializer = LabTestCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        test = serializer.save(ordered_by=request.user)
        return Response({
            'success': True,
            'message': 'Lab test created successfully',
            'test': LabTestSerializer(test).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': 'Failed to create lab test',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lab_test_detail_view(request, pk):
    """
    Get lab test details
    GET /api/lab-tests/<id>/
    """
    try:
        test = LabTest.objects.get(pk=pk)
        serializer = LabTestSerializer(test)
        return Response({
            'success': True,
            'test': serializer.data
        }, status=status.HTTP_200_OK)
    except LabTest.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Lab test not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def lab_test_update_view(request, pk):
    """
    Update lab test
    PUT/PATCH /api/lab-tests/<id>/update/
    """
    try:
        test = LabTest.objects.get(pk=pk)
        serializer = LabTestSerializer(test, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Lab test updated successfully',
                'test': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except LabTest.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Lab test not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def lab_test_delete_view(request, pk):
    """
    Delete lab test
    DELETE /api/lab-tests/<id>/delete/
    """
    try:
        test = LabTest.objects.get(pk=pk)
        test.delete()
        return Response({
            'success': True,
            'message': 'Lab test deleted successfully'
        }, status=status.HTTP_200_OK)
    except LabTest.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Lab test not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lab_test_category_list_view(request):
    """
    List all lab test categories or create a new one
    GET /api/lab-tests/categories/
    POST /api/lab-tests/categories/
    """
    if request.method == 'GET':
        categories = LabTestCategory.objects.filter(is_active=True).order_by('name')
        serializer = LabTestCategorySerializer(categories, many=True)
        return Response({
            'success': True,
            'categories': serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Only admin can create categories
        if request.user.role != 'admin' and not request.user.is_superuser:
            return Response({
                'success': False,
                'message': 'Permission denied. Admin access required.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = LabTestCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Category created successfully',
                'category': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def lab_test_category_detail_view(request, pk):
    """
    Update or delete a lab test category
    PUT/PATCH /api/lab-tests/categories/<id>/
    DELETE /api/lab-tests/categories/<id>/
    """
    # Only admin can modify categories
    if request.user.role != 'admin' and not request.user.is_superuser:
        return Response({
            'success': False,
            'message': 'Permission denied. Admin access required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        category = LabTestCategory.objects.get(pk=pk)
    except LabTestCategory.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Category not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'DELETE':
        category.delete()
        return Response({
            'success': True,
            'message': 'Category deleted successfully'
        }, status=status.HTTP_200_OK)
    
    serializer = LabTestCategorySerializer(category, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Category updated successfully',
            'category': serializer.data
        }, status=status.HTTP_200_OK)
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def lab_test_result_create_view(request, test_id):
    """
    Create a test result for a lab test
    POST /api/lab-tests/<test_id>/results/
    """
    try:
        test = LabTest.objects.get(pk=test_id)
    except LabTest.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Lab test not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    data = request.data.copy()
    data['test'] = test_id
    serializer = LabTestResultSerializer(data=data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Test result added successfully',
            'result': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def lab_test_result_detail_view(request, test_id, result_id):
    """
    Update or delete a test result
    PUT/PATCH /api/lab-tests/<test_id>/results/<result_id>/
    DELETE /api/lab-tests/<test_id>/results/<result_id>/
    """
    try:
        result = LabTestResult.objects.get(pk=result_id, test_id=test_id)
    except LabTestResult.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Test result not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'DELETE':
        result.delete()
        return Response({
            'success': True,
            'message': 'Test result deleted successfully'
        }, status=status.HTTP_200_OK)
    
    serializer = LabTestResultSerializer(result, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Test result updated successfully',
            'result': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lab_test_stats_view(request):
    """
    Get lab test statistics
    GET /api/lab-tests/stats/
    """
    if request.user.role != 'admin' and not request.user.is_superuser:
        return Response({
            'success': False,
            'message': 'Permission denied. Admin access required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Overall statistics
    total_tests = LabTest.objects.count()
    pending_tests = LabTest.objects.filter(status='pending').count()
    in_progress_tests = LabTest.objects.filter(status='in_progress').count()
    completed_tests = LabTest.objects.filter(status='completed').count()
    
    # Status breakdown
    tests_by_status = LabTest.objects.values('status').annotate(count=Count('status'))
    status_stats = {}
    for item in tests_by_status:
        status_stats[item['status']] = {
            'name': dict(LabTest.STATUS_CHOICES).get(item['status'], item['status']),
            'count': item['count']
        }
    
    # Priority breakdown
    tests_by_priority = LabTest.objects.values('priority').annotate(count=Count('priority'))
    priority_stats = {}
    for item in tests_by_priority:
        priority_stats[item['priority']] = {
            'name': dict(LabTest.PRIORITY_CHOICES).get(item['priority'], item['priority']),
            'count': item['count']
        }
    
    # Category breakdown
    tests_by_category = LabTest.objects.values('category__name').annotate(count=Count('category'))
    category_stats = {}
    for item in tests_by_category:
        if item['category__name']:
            category_stats[item['category__name']] = {
                'name': item['category__name'],
                'count': item['count']
            }
    
    return Response({
        'success': True,
        'stats': {
            'total_tests': total_tests,
            'pending_tests': pending_tests,
            'in_progress_tests': in_progress_tests,
            'completed_tests': completed_tests,
            'by_status': status_stats,
            'by_priority': priority_stats,
            'by_category': category_stats,
        }
    }, status=status.HTTP_200_OK)

