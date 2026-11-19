from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from databank.models import MarketData

class DataShare(models.Model):
    """
    Model representing dataset sharing permissions between users.
    Supports granular Role-Based Access Control (RBAC): Viewer and Editor.
    """
    class Permission(models.TextChoices):
        VIEWER = 'Viewer', 'Viewer (Read-only & Export access)'
        EDITOR = 'Editor', 'Editor (Can update dataset metrics)'

    dataset = models.ForeignKey(
        MarketData,
        on_delete=models.CASCADE,
        related_name='shares',
        help_text="Target dataset being shared"
    )
    shared_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shares_initiated',
        help_text="User who granted the share access"
    )
    shared_with = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shares_received',
        help_text="Recipient user receiving the share access"
    )
    permission = models.CharField(
        max_length=10,
        choices=Permission.choices,
        default=Permission.VIEWER,
        help_text="Granted permission level"
    )
    message = models.TextField(
        blank=True,
        help_text="Optional note or context message for the recipient"
    )
    shared_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Toggle to revoke or restore access"
    )

    class Meta:
        verbose_name = "Dataset Share Permission"
        verbose_name_plural = "Dataset Share Permissions"
        ordering = ['-shared_at']
        constraints = [
            # Ensure only one active share record per dataset & recipient
            models.UniqueConstraint(
                fields=['dataset', 'shared_with'],
                condition=models.Q(is_active=True),
                name='unique_active_dataset_share_recipient'
            )
        ]

    def clean(self):
        super().clean()
        if self.shared_with_id and self.shared_by_id:
            if self.shared_with_id == self.shared_by_id:
                raise ValidationError("You cannot share a dataset with yourself.")
        if self.dataset_id and self.shared_with_id:
            if self.dataset.created_by_id == self.shared_with_id:
                raise ValidationError("The recipient is already the owner of this dataset.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.dataset.title} shared with {self.shared_with.username} ({self.permission})"
