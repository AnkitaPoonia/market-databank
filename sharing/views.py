from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.http import url_has_allowed_host_and_scheme
from databank.models import MarketData, ActivityLog
from .models import DataShare
from .forms import DataShareForm

@login_required
def share_dataset_view(request, dataset_id):
    """
    Allow dataset owners to grant Viewer or Editor permissions to another registered user.
    """
    dataset = get_object_or_404(MarketData.objects.select_related('category', 'created_by'), pk=dataset_id)

    # Only owner or staff can share initially
    if dataset.created_by != request.user and not request.user.is_staff:
        raise PermissionDenied("Only the owner of this dataset has authority to grant sharing permissions.")

    if request.method == 'POST':
        form = DataShareForm(request.POST, dataset=dataset, current_user=request.user)
        if form.is_valid():
            share = form.save()

            # Audit activity log
            ActivityLog.objects.create(
                user=request.user,
                action='Shared Dataset',
                dataset=dataset,
                details=f"Shared '{dataset.title}' with {share.shared_with.username} as {share.permission}"
            )

            messages.success(
                request,
                f"Dataset '{dataset.title}' successfully shared with {share.shared_with.username} as {share.permission}!"
            )
            return redirect('databank:detail', pk=dataset.pk)
        else:
            messages.error(request, "Unable to share dataset. Please check the form errors below.")
    else:
        form = DataShareForm(dataset=dataset, current_user=request.user)

    existing_shares = DataShare.objects.filter(dataset=dataset, is_active=True).select_related('shared_with')

    context = {
        'form': form,
        'dataset': dataset,
        'existing_shares': existing_shares,
    }
    return render(request, 'sharing/share_form.html', context)


@login_required
def update_share_permission_view(request, share_id):
    """
    Allow dataset owners to update the permission level (Viewer <-> Editor) of an active collaborator.
    Requires POST.
    """
    share = get_object_or_404(DataShare.objects.select_related('dataset', 'shared_with'), pk=share_id)

    is_owner = (share.dataset.created_by == request.user or request.user.is_staff)
    if not is_owner:
        raise PermissionDenied("Only the dataset owner can change collaborator permissions.")

    if request.method == 'POST':
        new_permission = request.POST.get('permission', '').strip()
        if new_permission in [DataShare.Permission.VIEWER, DataShare.Permission.EDITOR]:
            old_permission = share.permission
            share.permission = new_permission
            share.save()

            ActivityLog.objects.create(
                user=request.user,
                action='Updated Share Permission',
                dataset=share.dataset,
                details=f"Changed {share.shared_with.username}'s permission from {old_permission} to {new_permission} on '{share.dataset.title}'"
            )

            messages.success(
                request,
                f"Successfully updated {share.shared_with.username}'s access to '{new_permission}'!"
            )
        else:
            messages.error(request, "Invalid permission level selected.")

    next_url = request.POST.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect('databank:detail', pk=share.dataset.pk)


@login_required
def shared_with_me_view(request):
    """
    Display all datasets that other users have shared with the currently logged-in user.
    """
    query = request.GET.get('q', '').strip()
    perm_filter = request.GET.get('permission', '')

    shares = DataShare.objects.filter(
        shared_with=request.user,
        is_active=True
    ).select_related('dataset', 'shared_by', 'dataset__category')

    if query:
        shares = shares.filter(
            Q(dataset__title__icontains=query) |
            Q(dataset__company_name__icontains=query) |
            Q(shared_by__username__icontains=query)
        )

    if perm_filter:
        shares = shares.filter(permission=perm_filter)

    paginator = Paginator(shares, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'selected_query': query,
        'selected_permission': perm_filter,
        'total_count': shares.count(),
    }
    return render(request, 'sharing/shared_with_me.html', context)


@login_required
def revoke_share_view(request, share_id):
    """
    Revoke a previously granted sharing permission.
    Restricted to dataset owner or staff. Requires POST.
    """
    share = get_object_or_404(DataShare.objects.select_related('dataset', 'shared_with', 'shared_by'), pk=share_id)

    is_owner = (share.dataset.created_by == request.user or request.user.is_staff)
    if not is_owner:
        raise PermissionDenied("Only the dataset owner can revoke collaborator permissions.")

    if request.method == 'POST':
        recipient_username = share.shared_with.username
        dataset_title = share.dataset.title
        dataset_id = share.dataset.pk

        # Mark inactive
        share.is_active = False
        share.save()

        ActivityLog.objects.create(
            user=request.user,
            action='Revoked Share Access',
            dataset=share.dataset,
            details=f"Revoked sharing access for {recipient_username} on '{dataset_title}'"
        )

        messages.info(request, f"Access for {recipient_username} on '{dataset_title}' has been revoked.")

        next_url = request.POST.get('next')
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect('databank:detail', pk=dataset_id)

    return redirect('databank:detail', pk=share.dataset.pk)
