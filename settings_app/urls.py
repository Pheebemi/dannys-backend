from django.urls import path
from . import views

app_name = 'settings_app'

urlpatterns = [
    path('', views.get_settings_view, name='get_settings'),
    path('update/', views.update_settings_view, name='update_settings'),
]

