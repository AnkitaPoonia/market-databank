from django.contrib import admin
from .models import DataShare

@admin.register(DataShare)
class DataShareAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'shared_by', 'shared_with', 'permission', 'is_active', 'shared_at')
    list_filter = ('permission', 'is_active', 'shared_at')
    search_fields = ('dataset__title', 'shared_by__username', 'shared_with__username', 'message')
    ordering = ('-shared_at',)
    readonly_fields = ('shared_at',)
