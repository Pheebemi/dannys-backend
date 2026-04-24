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
    path('services/create/', views.service_create_view, name='service_create'),
    path('services/<int:pk>/update/', views.service_update_view, name='service_update'),
    path('services/<int:pk>/delete/', views.service_delete_view, name='service_delete'),
    path('stats/', views.billing_stats_view, name='billing_stats'),
    path('tariffs/', views.tariff_list_view, name='tariff_list'),
    path('tariffs/create/', views.tariff_create_view, name='tariff_create'),
    path('tariffs/for-patient/<int:patient_id>/', views.tariff_for_patient_view, name='tariff_for_patient'),
    path('tariffs/<int:pk>/update/', views.tariff_update_view, name='tariff_update'),
    path('tariffs/<int:pk>/delete/', views.tariff_delete_view, name='tariff_delete'),
]

