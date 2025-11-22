from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Invoice, InvoiceItem, Payment, Service
from .serializers import (
    InvoiceSerializer, InvoiceCreateSerializer, InvoiceItemSerializer,
    PaymentSerializer, PaymentCreateSerializer, ServiceSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoice_list_view(request):
    """
    List all invoices with filtering
    GET /api/billing/invoices/
    Query Params:
        status (str): Filter by status
        patient_id (int): Filter by patient
        start_date (YYYY-MM-DD): Start date
        end_date (YYYY-MM-DD): End date
        page (int): Page number
        page_size (int): Items per page
    """
    invoices = Invoice.objects.all().order_by('-invoice_date', '-created_at')
    
    # Filters
    status_filter = request.query_params.get('status')
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    patient_id = request.query_params.get('patient_id')
    if patient_id:
        invoices = invoices.filter(patient_id=patient_id)
    
    start_date = request.query_params.get('start_date')
    if start_date:
        from datetime import datetime
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        invoices = invoices.filter(invoice_date__gte=start_date)
    
    end_date = request.query_params.get('end_date')
    if end_date:
        from datetime import datetime
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        invoices = invoices.filter(invoice_date__lte=end_date)
    
    # Pagination
    page_number = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    
    total_invoices = invoices.count()
    paginated_invoices = invoices[start_index:end_index]
    
    serializer = InvoiceSerializer(paginated_invoices, many=True)
    return Response({
        'success': True,
        'invoices': serializer.data,
        'pagination': {
            'total': total_invoices,
            'page': page_number,
            'page_size': page_size,
            'total_pages': (total_invoices + page_size - 1) // page_size,
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invoice_create_view(request):
    """
    Create a new invoice
    POST /api/billing/invoices/create/
    """
    serializer = InvoiceCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        invoice = serializer.save(created_by=request.user)
        return Response({
            'success': True,
            'message': 'Invoice created successfully',
            'invoice': InvoiceSerializer(invoice).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': 'Failed to create invoice',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoice_detail_view(request, pk):
    """
    Get invoice details
    GET /api/billing/invoices/<id>/
    """
    try:
        invoice = Invoice.objects.get(pk=pk)
        serializer = InvoiceSerializer(invoice)
        return Response({
            'success': True,
            'invoice': serializer.data
        }, status=status.HTTP_200_OK)
    except Invoice.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Invoice not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def invoice_update_view(request, pk):
    """
    Update invoice
    PUT/PATCH /api/billing/invoices/<id>/update/
    """
    try:
        invoice = Invoice.objects.get(pk=pk)
        serializer = InvoiceSerializer(invoice, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Invoice updated successfully',
                'invoice': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except Invoice.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Invoice not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def invoice_delete_view(request, pk):
    """
    Delete invoice
    DELETE /api/billing/invoices/<id>/delete/
    """
    try:
        invoice = Invoice.objects.get(pk=pk)
        invoice.delete()
        return Response({
            'success': True,
            'message': 'Invoice deleted successfully'
        }, status=status.HTTP_200_OK)
    except Invoice.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Invoice not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def payment_create_view(request):
    """
    Create a payment for an invoice
    POST /api/billing/payments/create/
    """
    serializer = PaymentCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        payment = serializer.save(processed_by=request.user)
        return Response({
            'success': True,
            'message': 'Payment recorded successfully',
            'payment': PaymentSerializer(payment).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': 'Failed to record payment',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def service_list_view(request):
    """
    List all services
    GET /api/billing/services/
    """
    services = Service.objects.filter(is_active=True).order_by('name')
    serializer = ServiceSerializer(services, many=True)
    return Response({
        'success': True,
        'services': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def billing_stats_view(request):
    """
    Get billing statistics
    GET /api/billing/stats/
    """
    if request.user.role != 'admin' and not request.user.is_superuser:
        return Response({
            'success': False,
            'message': 'Permission denied. Admin access required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Overall statistics
    total_invoices = Invoice.objects.count()
    total_revenue = Invoice.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_paid = Invoice.objects.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
    total_pending = total_revenue - total_paid
    
    # Status breakdown
    invoices_by_status = Invoice.objects.values('status').annotate(count=Count('status'))
    status_stats = {}
    for item in invoices_by_status:
        status_stats[item['status']] = {
            'name': dict(Invoice.STATUS_CHOICES).get(item['status'], item['status']),
            'count': item['count']
        }
    
    # Recent revenue (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_revenue = Invoice.objects.filter(
        invoice_date__gte=thirty_days_ago
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Monthly revenue trend (last 6 months)
    monthly_revenue = []
    for i in range(5, -1, -1):
        month_start = timezone.now().date().replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        revenue = Invoice.objects.filter(
            invoice_date__gte=month_start,
            invoice_date__lte=month_end
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        monthly_revenue.append({
            'month': month_start.strftime('%Y-%m'),
            'revenue': float(revenue)
        })
    
    return Response({
        'success': True,
        'stats': {
            'total_invoices': total_invoices,
            'total_revenue': float(total_revenue),
            'total_paid': float(total_paid),
            'total_pending': float(total_pending),
            'recent_revenue': float(recent_revenue),
            'by_status': status_stats,
            'monthly_revenue': monthly_revenue,
        }
    }, status=status.HTTP_200_OK)

