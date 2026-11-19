import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg, Min, Max
from django.db.models.functions import TruncMonth, TruncDate
from databank.models import MarketData, Category

@login_required
def analytics_dashboard_view(request):
    """
    Market intelligence analytics dashboard computing real aggregate metrics across the databank.
    """
    # High-level aggregate statistics
    total_datasets = MarketData.objects.count()
    total_categories = Category.objects.count()
    total_companies = MarketData.objects.values('company_name').distinct().count()
    avg_price_overall = MarketData.objects.aggregate(avg=Avg('market_price'))['avg'] or 0.0

    # 1. Industry Category Distribution
    category_counts = (
        MarketData.objects.values('category__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    cat_labels = [c['category__name'] for c in category_counts]
    cat_data = [c['count'] for c in category_counts]

    # 2. Market Demand Breakdown
    demand_counts = (
        MarketData.objects.values('market_demand')
        .annotate(count=Count('id'))
    )
    demand_dict = {d['market_demand']: d['count'] for d in demand_counts}
    demand_labels = ['High Demand', 'Medium Demand', 'Low Demand']
    demand_data = [
        demand_dict.get('High', 0),
        demand_dict.get('Medium', 0),
        demand_dict.get('Low', 0)
    ]

    # 3. Top Represented Companies
    company_counts = (
        MarketData.objects.values('company_name')
        .annotate(count=Count('id'))
        .order_by('-count')[:7]
    )
    company_labels = [c['company_name'] for c in company_counts]
    company_data = [c['count'] for c in company_counts]

    # 4. Average Benchmark Price by Sector
    price_by_cat = (
        MarketData.objects.values('category__name')
        .annotate(avg_price=Avg('market_price'))
        .order_by('-avg_price')[:6]
    )
    price_cat_labels = [p['category__name'] for p in price_by_cat]
    price_cat_data = [round(float(p['avg_price']), 2) for p in price_by_cat]

    # 5. Timeline / Creation Trends by Month
    trends = (
        MarketData.objects.annotate(period=TruncMonth('created_at'))
        .values('period')
        .annotate(count=Count('id'))
        .order_by('period')
    )
    timeline_labels = [t['period'].strftime('%b %Y') for t in trends if t['period']]
    timeline_data = [t['count'] for t in trends if t['period']]

    context = {
        'total_datasets': total_datasets,
        'total_categories': total_categories,
        'total_companies': total_companies,
        'avg_price_overall': avg_price_overall,
        'cat_labels_json': json.dumps(cat_labels),
        'cat_data_json': json.dumps(cat_data),
        'demand_labels_json': json.dumps(demand_labels),
        'demand_data_json': json.dumps(demand_data),
        'company_labels_json': json.dumps(company_labels),
        'company_data_json': json.dumps(company_data),
        'price_cat_labels_json': json.dumps(price_cat_labels),
        'price_cat_data_json': json.dumps(price_cat_data),
        'timeline_labels_json': json.dumps(timeline_labels),
        'timeline_data_json': json.dumps(timeline_data),
    }
    return render(request, 'analytics/analytics.html', context)


@login_required
def analytics_api_view(request):
    """
    JSON API returning market summary analytics for dynamic consumption or external charts.
    """
    category_counts = list(
        MarketData.objects.values('category__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    demand_counts = list(
        MarketData.objects.values('market_demand')
        .annotate(count=Count('id'))
    )
    return JsonResponse({
        'total_datasets': MarketData.objects.count(),
        'categories': category_counts,
        'demand': demand_counts,
    })
