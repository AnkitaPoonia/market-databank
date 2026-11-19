from django import forms
import datetime
from django.utils import timezone
from .models import MarketData, Category

class MarketDataForm(forms.ModelForm):
    """
    Form for creating and updating Market Datasets.
    Provides styling with Bootstrap classes and custom validation.
    """
    class Meta:
        model = MarketData
        fields = [
            'title',
            'company_name',
            'category',
            'industry',
            'product_service',
            'market_price',
            'market_demand',
            'market_size',
            'market_growth_rate',
            'description',
            'data_source',
            'collection_date',
            'visibility',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Q3 Electric Commercial Vehicle Market Intelligence'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Tata Motors Limited'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'industry': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Automotive & EV Manufacturing'
            }),
            'product_service': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Heavy Duty EV Cargo Fleets'
            }),
            'market_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'market_demand': forms.Select(attrs={
                'class': 'form-select'
            }),
            'market_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 52000000.00 (in USD)',
                'step': '0.01',
                'min': '0'
            }),
            'market_growth_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 14.50 (in %)',
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Detailed market findings, demand triggers, competitive landscape, regulatory drivers...'
            }),
            'data_source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Ministry of Road Transport Report, Company Annual Filing 2024'
            }),
            'collection_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'visibility': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def clean_collection_date(self):
        c_date = self.cleaned_data.get('collection_date')
        if c_date:
            max_allowed_today = max(timezone.now().date(), datetime.date.today())
            if c_date > max_allowed_today:
                raise forms.ValidationError("Data collection date cannot be in the future.")
        return c_date

    def clean_market_price(self):
        price = self.cleaned_data.get('market_price')
        if price is not None and price < 0:
            raise forms.ValidationError("Market price cannot be negative.")
        return price

