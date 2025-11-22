from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('invoices/', views.invoice_list_view, name='invoice_list'),
    path('invoices/create/', views.invoice_create_view, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail_view, name='invoice_detail'),
    path('invoices/<int:pk>/update/', views.invoice_update_view, name='invoice_update'),
    path('invoices/<int:pk>/delete/', views.invoice_delete_view, name='invoice_delete'),
    path('payments/create/', views.payment_create_view, name='payment_create'),
    path('services/', views.service_list_view, name='service_list'),
    path('stats/', views.billing_stats_view, name='billing_stats'),
]

