from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard_view, name='dashboard'),
    path('api/data/', views.analytics_api_view, name='api_data'),
]

