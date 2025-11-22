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
]

