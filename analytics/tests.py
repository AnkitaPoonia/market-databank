import datetime
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from databank.models import Category, MarketData

class AnalyticsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='analyst', password='Password123!')
        self.cat1 = Category.objects.create(name='Automotive')
        self.cat2 = Category.objects.create(name='Banking')

        MarketData.objects.create(
            title='Auto Report',
            company_name='Tesla',
            category=self.cat1,
            industry='EV',
            product_service='Sedan',
            market_price=Decimal('50000.00'),
            market_demand='High',
            description='Report',
            data_source='Source',
            collection_date=datetime.date.today(),
            visibility='Public',
            created_by=self.user
        )

        MarketData.objects.create(
            title='Bank Report',
            company_name='JPMorgan',
            category=self.cat2,
            industry='Finance',
            product_service='Credit',
            market_price=Decimal('100.00'),
            market_demand='Medium',
            description='Report',
            data_source='Source',
            collection_date=datetime.date.today(),
            visibility='Public',
            created_by=self.user
        )

    def test_analytics_dashboard_requires_login(self):
        response = self.client.get(reverse('analytics:dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_analytics_dashboard_renders_metrics(self):
        self.client.login(username='analyst', password='Password123!')
        response = self.client.get(reverse('analytics:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Market Analytics')
        self.assertEqual(response.context['total_datasets'], 2)
        self.assertEqual(response.context['total_companies'], 2)

    def test_analytics_api_endpoint(self):
        self.client.login(username='analyst', password='Password123!')
        response = self.client.get(reverse('analytics:api_data'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['total_datasets'], 2)
        self.assertEqual(len(data['categories']), 2)
