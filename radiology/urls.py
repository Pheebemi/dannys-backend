from django.urls import path
from . import views

urlpatterns = [
    path('', views.radiology_test_list_view, name='radiology-list'),
    path('create/', views.radiology_test_create_view, name='radiology-create'),
    path('<int:pk>/', views.radiology_test_detail_view, name='radiology-detail'),
    path('<int:pk>/update/', views.radiology_test_update_view, name='radiology-update'),
    path('<int:pk>/delete/', views.radiology_test_delete_view, name='radiology-delete'),
    path('categories/', views.radiology_category_list_view, name='radiology-categories'),
    path('stats/', views.radiology_stats_view, name='radiology-stats'),
    path('<int:test_id>/results/', views.radiology_result_create_view, name='radiology-result-create'),
    path('<int:test_id>/results/<int:result_id>/', views.radiology_result_detail_view, name='radiology-result-detail'),
]
