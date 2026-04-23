from django.urls import path
from . import views

urlpatterns = [
    path('', views.appointment_list_view, name='appointment-list'),
    path('create/', views.appointment_create_view, name='appointment-create'),
    path('stats/', views.appointment_stats_view, name='appointment-stats'),
    path('<int:pk>/', views.appointment_detail_view, name='appointment-detail'),
    path('<int:pk>/update/', views.appointment_update_view, name='appointment-update'),
    path('<int:pk>/delete/', views.appointment_delete_view, name='appointment-delete'),
    path('<int:pk>/checkin/', views.appointment_checkin_view, name='appointment-checkin'),
]
