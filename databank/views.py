import csv
import io
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.db.models import Q, Count
from django.utils import timezone
from .models import MarketData, Category, ActivityLog
from .forms import MarketDataForm
from sharing.models import DataShare


def home_view(request):
    """
    Public landing page introducing the platform with real database preview.
    """
    recent_public = MarketData.objects.filter(visibility=MarketData.Visibility.PUBLIC).select_related('category', 'created_by')[:3]
    total_public_count = MarketData.objects.filter(visibility=MarketData.Visibility.PUBLIC).count()
    total_categories = Category.objects.count()

    context = {
        'recent_public': recent_public,
        'total_public_count': total_public_count,
        'total_categories': total_categories,
        'hide_sidebar': True,
    }
    return render(request, 'home.html', context)


@login_required
def dashboard_view(request):
    """
    User dashboard displaying personal statistics, recent activities, and Chart.js analytics.
    """
    user = request.user

    # Database-driven metrics
    my_datasets_count = MarketData.objects.filter(created_by=user).count()
    shared_with_me_count = DataShare.objects.filter(shared_with=user, is_active=True).count()
    total_public_count = MarketData.objects.filter(visibility=MarketData.Visibility.PUBLIC).count()
    total_categories_count = Category.objects.count()

    # Recent datasets created by user
    recent_datasets = MarketData.objects.filter(created_by=user).select_related('category')[:5]

    # Recent activity logs for user
    recent_activities = ActivityLog.objects.filter(user=user).select_related('dataset')[:6]

    # Chart 1: Datasets by Category (User's datasets or platform if user has few)
    user_cat_data = (
        MarketData.objects.filter(created_by=user)
        .values('category__name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    cat_labels = [item['category__name'] for item in user_cat_data]
    cat_values = [item['total'] for item in user_cat_data]

    # Chart 2: Market Demand Distribution for User
    demand_data = (
        MarketData.objects.filter(created_by=user)
        .values('market_demand')
        .annotate(total=Count('id'))
    )
    demand_dict = {item['market_demand']: item['total'] for item in demand_data}
    demand_labels = ['High', 'Medium', 'Low']
    demand_values = [
        demand_dict.get('High', 0),
        demand_dict.get('Medium', 0),
        demand_dict.get('Low', 0)
    ]

    context = {
        'my_datasets_count': my_datasets_count,
        'shared_with_me_count': shared_with_me_count,
        'total_public_count': total_public_count,
        'total_categories_count': total_categories_count,
        'recent_datasets': recent_datasets,
        'recent_activities': recent_activities,
        'cat_labels_json': json.dumps(cat_labels),
        'cat_values_json': json.dumps(cat_values),
        'demand_labels_json': json.dumps(demand_labels),
        'demand_values_json': json.dumps(demand_values),
    }
    return render(request, 'databank/dashboard.html', context)


@login_required
def create_dataset_view(request):
    """
    Handle creation of a new market dataset record.
    Ensures creator is automatically assigned and logged.
    """
    if request.method == 'POST':
        form = MarketDataForm(request.POST)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.created_by = request.user
            dataset.save()

            # Record audit trail in ActivityLog
            ActivityLog.objects.create(
                user=request.user,
                action='Created Dataset',
                dataset=dataset,
                details=f"Created '{dataset.title}' for {dataset.company_name} ({dataset.visibility})"
            )

            messages.success(request, f"Market dataset '{dataset.title}' created successfully!")
            return redirect('databank:detail', pk=dataset.pk)
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = MarketDataForm()

    return render(request, 'databank/create_dataset.html', {'form': form})


@login_required
def my_datasets_view(request):
    """
    Display all datasets owned by the logged-in user with search, filtering, and pagination.
    """
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    demand = request.GET.get('demand', '')
    visibility = request.GET.get('visibility', '')

    datasets = MarketData.objects.filter(created_by=request.user).select_related('category')

    if query:
        datasets = datasets.filter(
            Q(title__icontains=query) |
            Q(company_name__icontains=query) |
            Q(industry__icontains=query) |
            Q(product_service__icontains=query)
        )

    if category_id:
        datasets = datasets.filter(category_id=category_id)

    if demand:
        datasets = datasets.filter(market_demand=demand)

    if visibility:
        datasets = datasets.filter(visibility=visibility)

    paginator = Paginator(datasets, 8)  # 8 datasets per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_query': query,
        'selected_category': category_id,
        'selected_demand': demand,
        'selected_visibility': visibility,
        'total_count': datasets.count(),
    }
    return render(request, 'databank/my_datasets.html', context)


def explore_view(request):
    """
    Explore accessible market datasets across the databank.
    Public datasets are accessible to all; private datasets require ownership or explicit share.
    """
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    demand = request.GET.get('demand', '')
    sort_by = request.GET.get('sort', '-created_at')

    # Security scoping: filter only datasets the current user has rights to see
    if request.user.is_authenticated:
        shared_dataset_ids = DataShare.objects.filter(
            shared_with=request.user,
            is_active=True
        ).values_list('dataset_id', flat=True)

        base_filter = (
            Q(visibility=MarketData.Visibility.PUBLIC) |
            Q(created_by=request.user) |
            Q(id__in=shared_dataset_ids)
        )
    else:
        # Guests can only see public datasets
        base_filter = Q(visibility=MarketData.Visibility.PUBLIC)

    datasets = MarketData.objects.filter(base_filter).select_related('category', 'created_by')

    if query:
        datasets = datasets.filter(
            Q(title__icontains=query) |
            Q(company_name__icontains=query) |
            Q(industry__icontains=query) |
            Q(product_service__icontains=query)
        )

    if category_id:
        datasets = datasets.filter(category_id=category_id)

    if demand:
        datasets = datasets.filter(market_demand=demand)

    # Sorting
    allowed_sorts = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'price_low': 'market_price',
        'price_high': '-market_price',
        'title': 'title',
    }
    sort_field = allowed_sorts.get(sort_by, '-created_at')
    datasets = datasets.order_by(sort_field)

    paginator = Paginator(datasets, 9)  # 9 per page for a 3x3 grid
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_query': query,
        'selected_category': category_id,
        'selected_demand': demand,
        'selected_sort': sort_by,
        'total_count': datasets.count(),
        'hide_sidebar': not request.user.is_authenticated,
    }
    return render(request, 'databank/explore.html', context)


def dataset_detail_view(request, pk):
    """
    Detailed dataset page with strict RBAC permission inspection.
    """
    dataset = get_object_or_404(MarketData.objects.select_related('category', 'created_by'), pk=pk)

    # Check read permissions
    is_authenticated = request.user.is_authenticated
    is_owner = is_authenticated and (dataset.created_by == request.user or request.user.is_staff)

    share_record = None
    if is_authenticated and not is_owner:
        share_record = DataShare.objects.filter(
            dataset=dataset,
            shared_with=request.user,
            is_active=True
        ).first()

    has_read_access = (
        dataset.visibility == MarketData.Visibility.PUBLIC or
        is_owner or
        share_record is not None
    )

    if not has_read_access:
        raise PermissionDenied("You do not have permission to view this private dataset.")

    can_edit = is_owner or (share_record is not None and share_record.permission == DataShare.Permission.EDITOR)
    can_delete = is_owner
    can_share = is_owner

    # If owner, fetch list of active shares for this dataset
    active_shares = []
    if is_owner:
        active_shares = DataShare.objects.filter(dataset=dataset, is_active=True).select_related('shared_with')

    context = {
        'dataset': dataset,
        'is_owner': is_owner,
        'can_edit': can_edit,
        'can_delete': can_delete,
        'can_share': can_share,
        'share_record': share_record,
        'active_shares': active_shares,
        'hide_sidebar': not is_authenticated,
    }
    return render(request, 'databank/dataset_detail.html', context)


@login_required
def edit_dataset_view(request, pk):
    """
    Allow dataset owners and authorized editors to update records.
    Preserves original creator and logs updates.
    """
    dataset = get_object_or_404(MarketData, pk=pk)

    is_owner = (dataset.created_by == request.user or request.user.is_staff)
    is_editor = DataShare.objects.filter(
        dataset=dataset,
        shared_with=request.user,
        permission=DataShare.Permission.EDITOR,
        is_active=True
    ).exists()

    if not (is_owner or is_editor):
        raise PermissionDenied("You do not have Editor permissions to modify this dataset.")

    if request.method == 'POST':
        form = MarketDataForm(request.POST, instance=dataset)
        if form.is_valid():
            # Ensure creator is not overridden
            updated_dataset = form.save()

            ActivityLog.objects.create(
                user=request.user,
                action='Updated Dataset',
                dataset=updated_dataset,
                details=f"Modified dataset metrics for '{updated_dataset.title}'"
            )

            messages.success(request, f"Market dataset '{updated_dataset.title}' updated successfully.")
            return redirect('databank:detail', pk=updated_dataset.pk)
        else:
            messages.error(request, "Please fix the validation errors below.")
    else:
        form = MarketDataForm(instance=dataset)

    context = {
        'form': form,
        'dataset': dataset,
        'is_owner': is_owner,
    }
    return render(request, 'databank/edit_dataset.html', context)


@login_required
def delete_dataset_view(request, pk):
    """
    Confirm and process deletion of a dataset.
    Strictly limited to the dataset owner or staff administrator. Requires POST.
    """
    dataset = get_object_or_404(MarketData, pk=pk)

    is_owner = (dataset.created_by == request.user or request.user.is_staff)
    if not is_owner:
        raise PermissionDenied("Only the dataset owner or administrator can delete this dataset.")

    if request.method == 'POST':
        dataset_title = dataset.title
        dataset_company = dataset.company_name
        dataset.delete()

        ActivityLog.objects.create(
            user=request.user,
            action='Deleted Dataset',
            dataset=None,
            details=f"Permanently removed dataset '{dataset_title}' ({dataset_company})"
        )

        messages.success(request, f"Dataset '{dataset_title}' has been successfully deleted.")
        return redirect('databank:my_datasets')

    return render(request, 'databank/delete_confirm.html', {'dataset': dataset})


def sanitize_csv_cell(value):
    """
    Sanitize values to prevent Formula Injection (CSV Injection) attacks.
    Values starting with '=', '+', '-', or '@' are prepended with an apostrophe.
    """
    if value is None:
        return ""
    val_str = str(value)
    if val_str.startswith(('=', '+', '-', '@')):
        return "'" + val_str
    return val_str


def export_dataset_csv_view(request, pk):
    """
    Generate and download sanitized CSV for an authorized dataset.
    """
    dataset = get_object_or_404(MarketData.objects.select_related('category', 'created_by'), pk=pk)

    # Permission check
    is_authenticated = request.user.is_authenticated
    is_owner = is_authenticated and (dataset.created_by == request.user or request.user.is_staff)

    has_share = False
    if is_authenticated and not is_owner:
        has_share = DataShare.objects.filter(
            dataset=dataset,
            shared_with=request.user,
            is_active=True
        ).exists()

    if not (dataset.visibility == MarketData.Visibility.PUBLIC or is_owner or has_share):
        raise PermissionDenied("You are not authorized to download this private dataset.")

    # Generate CSV response
    safe_filename = "".join([c if c.isalnum() else "_" for c in dataset.title])[:40]
    filename = f"MarketDatabank_{safe_filename}_{dataset.pk}.csv"

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Write UTF-8 BOM for seamless Microsoft Excel compatibility with Unicode characters
    response.write('\ufeff')

    writer = csv.writer(response)
    # Header row
    writer.writerow([
        'ID',
        'Title',
        'Company Name',
        'Category',
        'Industry',
        'Product/Service',
        'Market Price',
        'Market Demand',
        'Market Size',
        'Growth Rate (%)',
        'Description',
        'Data Source',
        'Collection Date',
        'Visibility',
        'Creator',
        'Created At',
        'Updated At'
    ])

    # Data row with sanitization
    writer.writerow([
        sanitize_csv_cell(dataset.pk),
        sanitize_csv_cell(dataset.title),
        sanitize_csv_cell(dataset.company_name),
        sanitize_csv_cell(dataset.category.name if dataset.category else ""),
        sanitize_csv_cell(dataset.industry),
        sanitize_csv_cell(dataset.product_service),
        sanitize_csv_cell(dataset.market_price),
        sanitize_csv_cell(dataset.market_demand),
        sanitize_csv_cell(dataset.market_size or "N/A"),
        sanitize_csv_cell(dataset.market_growth_rate or "N/A"),
        sanitize_csv_cell(dataset.description),
        sanitize_csv_cell(dataset.data_source),
        sanitize_csv_cell(dataset.collection_date),
        sanitize_csv_cell(dataset.visibility),
        sanitize_csv_cell(dataset.created_by.username),
        sanitize_csv_cell(dataset.created_at.strftime('%Y-%m-%d %H:%M:%S')),
        sanitize_csv_cell(dataset.updated_at.strftime('%Y-%m-%d %H:%M:%S')),
    ])

    # Log the export action if user is authenticated
    if is_authenticated:
        ActivityLog.objects.create(
            user=request.user,
            action='Exported CSV',
            dataset=dataset,
            details=f"Downloaded CSV export for '{dataset.title}'"
        )

    return response


def export_dataset_pdf_view(request, pk):
    """
    Generate and download publication-quality PDF dossier for an authorized dataset.
    Built with ReportLab Platypus engine.
    """
    from .reports import generate_dataset_pdf

    dataset = get_object_or_404(MarketData.objects.select_related('category', 'created_by'), pk=pk)

    # Permission check (matches CSV permissions exactly)
    is_authenticated = request.user.is_authenticated
    is_owner = is_authenticated and (dataset.created_by == request.user or request.user.is_staff)

    has_share = False
    if is_authenticated and not is_owner:
        has_share = DataShare.objects.filter(
            dataset=dataset,
            shared_with=request.user,
            is_active=True
        ).exists()

    if not (dataset.visibility == MarketData.Visibility.PUBLIC or is_owner or has_share):
        raise PermissionDenied("You are not authorized to download this private dataset report.")

    # Generate PDF in-memory buffer
    buffer = io.BytesIO()
    try:
        generate_dataset_pdf(dataset, buffer)
    except Exception as e:
        messages.error(request, f"Unable to generate PDF report: {str(e)}")
        return redirect('databank:detail', pk=dataset.pk)

    buffer.seek(0)

    safe_filename = "".join([c if c.isalnum() else "_" for c in dataset.title])[:40]
    filename = f"MarketDatabank_{safe_filename}_{dataset.pk}.pdf"

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Audit export action in ActivityLog
    if is_authenticated:
        ActivityLog.objects.create(
            user=request.user,
            action='Exported PDF',
            dataset=dataset,
            details=f"Downloaded PDF report for '{dataset.title}'"
        )

    return response


def custom_403_view(request, exception=None):
    return render(request, '403.html', status=403)


def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)


def custom_500_view(request):
    return render(request, '500.html', status=500)
