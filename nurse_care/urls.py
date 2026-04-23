from django.urls import path
from . import views

urlpatterns = [
    # Vital Signs
    path('vital-signs/', views.vital_sign_list_view, name='vital-sign-list'),
    path('vital-signs/create/', views.vital_sign_create_view, name='vital-sign-create'),
    path('vital-signs/stats/', views.vital_sign_stats_view, name='vital-sign-stats'),
    path('vital-signs/<int:pk>/', views.vital_sign_detail_view, name='vital-sign-detail'),
    # Medication Records
    path('medications/', views.medication_list_view, name='medication-list'),
    path('medications/create/', views.medication_create_view, name='medication-create'),
    path('medications/stats/', views.medication_stats_view, name='medication-stats'),
    path('medications/<int:pk>/', views.medication_detail_view, name='medication-detail'),
    path('medications/<int:pk>/update/', views.medication_update_view, name='medication-update'),
    path('medications/<int:pk>/delete/', views.medication_delete_view, name='medication-delete'),
]
