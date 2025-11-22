from django.urls import path
from . import views

app_name = 'lab_tests'

urlpatterns = [
    path('', views.lab_test_list_view, name='lab_test_list'),
    path('create/', views.lab_test_create_view, name='lab_test_create'),
    path('<int:pk>/', views.lab_test_detail_view, name='lab_test_detail'),
    path('<int:pk>/update/', views.lab_test_update_view, name='lab_test_update'),
    path('<int:pk>/delete/', views.lab_test_delete_view, name='lab_test_delete'),
    path('<int:test_id>/results/', views.lab_test_result_create_view, name='lab_test_result_create'),
    path('<int:test_id>/results/<int:result_id>/', views.lab_test_result_detail_view, name='lab_test_result_detail'),
    path('categories/', views.lab_test_category_list_view, name='lab_test_categories'),
    path('categories/<int:pk>/', views.lab_test_category_detail_view, name='lab_test_category_detail'),
    path('stats/', views.lab_test_stats_view, name='lab_test_stats'),
]

