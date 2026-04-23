from django.urls import path
from . import views

urlpatterns = [
    # Prescriptions
    path('prescriptions/', views.prescription_list_view, name='prescription-list'),
    path('prescriptions/create/', views.prescription_create_view, name='prescription-create'),
    path('prescriptions/<int:pk>/', views.prescription_detail_view, name='prescription-detail'),
    path('prescriptions/<int:pk>/update/', views.prescription_update_view, name='prescription-update'),
    path('prescriptions/<int:pk>/delete/', views.prescription_delete_view, name='prescription-delete'),
    # Inventory
    path('inventory/', views.inventory_list_view, name='inventory-list'),
    path('inventory/create/', views.inventory_create_view, name='inventory-create'),
    path('inventory/<int:pk>/', views.inventory_detail_view, name='inventory-detail'),
    path('inventory/<int:pk>/update/', views.inventory_update_view, name='inventory-update'),
    path('inventory/<int:pk>/delete/', views.inventory_delete_view, name='inventory-delete'),
    # Stats
    path('stats/', views.pharmacy_stats_view, name='pharmacy-stats'),
]
