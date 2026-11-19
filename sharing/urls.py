from django.urls import path
from . import views

app_name = 'sharing'

urlpatterns = [
    path('shared-with-me/', views.shared_with_me_view, name='shared_with_me'),
    path('share/<int:dataset_id>/', views.share_dataset_view, name='share_dataset'),
    path('update/<int:share_id>/', views.update_share_permission_view, name='update_share'),
    path('revoke/<int:share_id>/', views.revoke_share_view, name='revoke_share'),
]
