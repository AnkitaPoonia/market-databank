from django.contrib import admin
from .models import Category, MarketData, ActivityLog

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(MarketData)
class MarketDataAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'company_name',
        'category',
        'industry',
        'market_price',
        'market_demand',
        'visibility',
        'created_by',
        'created_at'
    )
    list_filter = ('visibility', 'market_demand', 'category', 'industry', 'created_at')
    search_fields = ('title', 'company_name', 'product_service', 'industry', 'description', 'data_source')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('General Information', {
            'fields': ('title', 'company_name', 'category', 'industry', 'product_service')
        }),
        ('Market Economics & Valuation', {
            'fields': ('market_price', 'market_demand', 'market_size', 'market_growth_rate')
        }),
        ('Research & Provenance', {
            'fields': ('description', 'data_source', 'collection_date')
        }),
        ('Permissions & Ownership', {
            'fields': ('visibility', 'created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'dataset', 'details')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'action', 'details', 'dataset__title')
    ordering = ('-timestamp',)
    readonly_fields = ('user', 'action', 'dataset', 'details', 'timestamp')

    def has_add_permission(self, request):
        return False  # Activity logs are audit records, created automatically
