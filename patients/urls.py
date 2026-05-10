from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.patient_list_view, name='patient_list'),
    path('create/', views.patient_create_view, name='patient_create'),
    path('stats/', views.patient_stats_view, name='patient_stats'),
    path('<int:pk>/', views.patient_detail_view, name='patient_detail'),
    path('<int:pk>/update/', views.patient_update_view, name='patient_update'),
    path('<int:pk>/delete/', views.patient_delete_view, name='patient_delete'),
    path('<int:pk>/portal-status/', views.patient_portal_status_view, name='patient_portal_status'),
    # HMO
    path('hmos/', views.hmo_list_view, name='hmo_list'),
    path('hmos/create/', views.hmo_create_view, name='hmo_create'),
    path('hmos/<int:pk>/update/', views.hmo_update_view, name='hmo_update'),
    path('hmos/<int:pk>/delete/', views.hmo_delete_view, name='hmo_delete'),
    # Referral / Discharge
    path('referrals/', views.referral_list_view, name='referral_list'),
    path('referrals/create/', views.referral_create_view, name='referral_create'),
    path('referrals/<int:pk>/', views.referral_detail_view, name='referral_detail'),
    path('referrals/<int:pk>/delete/', views.referral_delete_view, name='referral_delete'),
]

