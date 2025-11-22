from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('analytics/', views.analytics_overview_view, name='analytics_overview'),
    path('staff/', views.staff_report_view, name='staff_report'),
    path('patients/', views.patient_report_view, name='patient_report'),
]

