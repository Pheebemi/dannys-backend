from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile_view, name='update_profile'),
    path('refresh/', views.refresh_token_view, name='refresh_token'),
    # Admin endpoints
    path('staff/', views.staff_list_view, name='staff_list'),
    path('staff/create/', views.staff_create_view, name='staff_create'),
    path('staff/stats/', views.staff_stats_view, name='staff_stats'),
    path('staff/<int:pk>/', views.staff_detail_view, name='staff_detail'),
    path('staff/<int:pk>/update/', views.staff_update_view, name='staff_update'),
    path('staff/<int:pk>/delete/', views.staff_delete_view, name='staff_delete'),
]

