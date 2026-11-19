"""
Root URL Configuration for market_databank project.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from databank.views import home_view, custom_403_view, custom_404_view, custom_500_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('databank/', include('databank.urls', namespace='databank')),
    path('sharing/', include('sharing.urls', namespace='sharing')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
]

handler403 = custom_403_view
handler404 = custom_404_view
handler500 = custom_500_view
