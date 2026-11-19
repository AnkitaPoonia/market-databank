from django.urls import path
from . import views

app_name = 'databank'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('explore/', views.explore_view, name='explore'),
    path('my-datasets/', views.my_datasets_view, name='my_datasets'),
    path('create/', views.create_dataset_view, name='create'),
    path('<int:pk>/', views.dataset_detail_view, name='detail'),
    path('<int:pk>/edit/', views.edit_dataset_view, name='edit'),
    path('<int:pk>/delete/', views.delete_dataset_view, name='delete'),
    path('<int:pk>/export/csv/', views.export_dataset_csv_view, name='export_csv'),
    path('<int:pk>/export/pdf/', views.export_dataset_pdf_view, name='export_pdf'),
]

