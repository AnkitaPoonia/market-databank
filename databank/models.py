from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse

class Category(models.Model):
    """
    Category model for organizing market datasets across industries and sectors.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Unique name of market category/sector")
    description = models.TextField(blank=True, help_text="Overview and scope of the category")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class MarketData(models.Model):
    """
    Core Market Dataset model storing structured intelligence metrics for companies and products.
    """
    class MarketDemand(models.TextChoices):
        LOW = 'Low', 'Low Demand'
        MEDIUM = 'Medium', 'Medium Demand'
        HIGH = 'High', 'High Demand'

    class Visibility(models.TextChoices):
        PRIVATE = 'Private', 'Private (Only Owner & Shared Users)'
        PUBLIC = 'Public', 'Public (Visible to All Registered Users)'

    title = models.CharField(max_length=200, help_text="Descriptive title of the market dataset")
    company_name = models.CharField(max_length=150, help_text="Target enterprise or entity name")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='datasets',
        help_text="Primary industry/sector category"
    )
    industry = models.CharField(max_length=100, help_text="Specific industry or niche segment")
    product_service = models.CharField(max_length=200, help_text="Product, service, or offering evaluated")
    
    market_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
        help_text="Standard unit price or average benchmark price in USD/INR"
    )
    market_demand = models.CharField(
        max_length=10,
        choices=MarketDemand.choices,
        default=MarketDemand.MEDIUM,
        help_text="Current demand trajectory assessment"
    )
    market_size = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        help_text="Estimated total addressable market size (e.g. in Millions)"
    )
    market_growth_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(-100.0), MaxValueValidator(1000.0)],
        help_text="Compound annual growth rate percentage (CAGR %)"
    )
    description = models.TextField(help_text="In-depth analysis, market conditions, and qualitative observations")
    data_source = models.CharField(max_length=255, help_text="Origin of data (e.g. Annual Report 2024, SEC Filing, Gartner)")
    collection_date = models.DateField(help_text="Date when information was recorded or published")
    visibility = models.CharField(
        max_length=10,
        choices=Visibility.choices,
        default=Visibility.PRIVATE,
        help_text="Dataset accessibility level"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_datasets',
        help_text="Account that created and owns this record"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Market Dataset"
        verbose_name_plural = "Market Datasets"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['company_name']),
            models.Index(fields=['industry']),
            models.Index(fields=['visibility']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.company_name}"

    def get_absolute_url(self):
        return reverse('databank:detail', kwargs={'pk': self.pk})

    def user_has_permission(self, user, required_perm='Viewer'):
        """
        Check if given user has the required permission for this dataset.
        Owner has all permissions ('Viewer', 'Editor', 'Owner').
        """
        if not user or not user.is_authenticated:
            return False
        if self.created_by == user or user.is_staff:
            return True

        if required_perm == 'Viewer' and self.visibility == self.Visibility.PUBLIC:
            return True

        # Check explicit share records
        from sharing.models import DataShare
        active_share = DataShare.objects.filter(
            dataset=self,
            shared_with=user,
            is_active=True
        ).first()

        if not active_share:
            return False

        if required_perm == 'Viewer':
            return True  # Both Viewer and Editor can view
        elif required_perm == 'Editor':
            return active_share.permission == DataShare.Permission.EDITOR

        return False


class ActivityLog(models.Model):
    """
    Audit and activity log tracking user actions across datasets (creation, updates, shares, exports).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    action = models.CharField(max_length=100, help_text="Action performed (e.g. Created Dataset, Exported CSV)")
    dataset = models.ForeignKey(
        MarketData,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='activity_logs'
    )
    details = models.TextField(blank=True, help_text="Additional metadata or context")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.user.username} - {self.action}"
