from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import DataShare
from databank.models import MarketData

class DataShareForm(forms.ModelForm):
    """
    Form to invite and authorize registered users as Viewers or Editors of a dataset.
    Automatically assigns dataset and owner (shared_by) on save.
    """
    recipient_identifier = forms.CharField(
        label="Recipient Username or Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter registered username or email address',
            'autocomplete': 'off'
        }),
        help_text="The recipient must already have an active registered account on Market Databank."
    )

    class Meta:
        model = DataShare
        fields = ['permission', 'message']
        widgets = {
            'permission': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional invitation message or briefing for the collaborator...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.dataset = kwargs.pop('dataset', None)
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

    def clean_recipient_identifier(self):
        ident = self.cleaned_data.get('recipient_identifier', '').strip()
        if not ident:
            raise ValidationError("Please provide a recipient username or email.")

        # Find user by username or email
        recipient = User.objects.filter(Q(username__iexact=ident) | Q(email__iexact=ident)).first()
        if not recipient:
            raise ValidationError(f"No registered user found matching '{ident}'. Ensure they have created an account.")

        if self.current_user and recipient == self.current_user:
            raise ValidationError("You cannot share a dataset with yourself.")

        if self.dataset and recipient == self.dataset.created_by:
            raise ValidationError(f"User '{recipient.username}' is already the owner of this dataset.")

        # Check for existing active share
        if self.dataset and DataShare.objects.filter(dataset=self.dataset, shared_with=recipient, is_active=True).exists():
            raise ValidationError(f"This dataset is already actively shared with '{recipient.username}'. You can modify their permission in the Manage Sharing section.")

        self.recipient_user = recipient
        return ident

    def save(self, commit=True):
        # Check if an inactive share record already exists (e.g. previously revoked)
        existing_inactive = DataShare.objects.filter(
            dataset=self.dataset,
            shared_with=self.recipient_user,
            is_active=False
        ).first()

        if existing_inactive:
            existing_inactive.permission = self.cleaned_data['permission']
            existing_inactive.message = self.cleaned_data.get('message', '')
            existing_inactive.shared_by = self.current_user
            existing_inactive.is_active = True
            if commit:
                existing_inactive.save()
            return existing_inactive

        instance = super().save(commit=False)
        instance.dataset = self.dataset
        instance.shared_by = self.current_user
        instance.shared_with = self.recipient_user
        instance.is_active = True
        if commit:
            instance.save()
        return instance
