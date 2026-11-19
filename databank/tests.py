import datetime
from decimal import Decimal
from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from databank.models import Category, MarketData, ActivityLog
from databank.views import sanitize_csv_cell

class DatabankManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='analyst1', password='Password123!')
        self.other_user = User.objects.create_user(username='analyst2', password='Password123!')
        self.category = Category.objects.create(name='Automobile', description='Automotive sector')

        self.dataset_data = {
            'title': 'EV Charging Market Analysis',
            'company_name': 'Tata Power',
            'category': self.category.id,
            'industry': 'Clean Energy Infrastructure',
            'product_service': 'Ultra-Fast EV Chargers',
            'market_price': '45000.00',
            'market_demand': 'High',
            'market_size': '2500000.00',
            'market_growth_rate': '24.50',
            'description': 'Rapid expansion of charging corridors along major highways.',
            'data_source': 'Ministry of Power 2024 Report',
            'collection_date': timezone.now().date().strftime('%Y-%m-%d'),
            'visibility': 'Public',
        }

    def test_create_dataset_view(self):
        self.client.login(username='analyst1', password='Password123!')
        response = self.client.post(reverse('databank:create'), self.dataset_data)
        self.assertEqual(response.status_code, 302)
        dataset = MarketData.objects.get(title='EV Charging Market Analysis')
        self.assertEqual(dataset.created_by, self.user)
        self.assertEqual(dataset.market_price, Decimal('45000.00'))
        # Ensure activity log was created
        self.assertTrue(ActivityLog.objects.filter(dataset=dataset, action='Created Dataset').exists())

    def test_view_public_dataset(self):
        dataset = MarketData.objects.create(
            title='Public Dataset',
            company_name='Public Corp',
            category=self.category,
            industry='Tech',
            product_service='Software',
            market_price=Decimal('100.00'),
            market_demand='High',
            description='Test',
            data_source='Source',
            collection_date=datetime.date.today(),
            visibility=MarketData.Visibility.PUBLIC,
            created_by=self.user
        )
        # Even unauthenticated or other user can view public dataset
        response = self.client.get(reverse('databank:detail', kwargs={'pk': dataset.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Public Dataset')

    def test_private_dataset_access_forbidden_to_stranger(self):
        private_dataset = MarketData.objects.create(
            title='Secret Strategy',
            company_name='Private Corp',
            category=self.category,
            industry='Tech',
            product_service='Secret Tech',
            market_price=Decimal('500.00'),
            market_demand='High',
            description='Proprietary notes',
            data_source='Internal',
            collection_date=datetime.date.today(),
            visibility=MarketData.Visibility.PRIVATE,
            created_by=self.user
        )
        self.client.login(username='analyst2', password='Password123!')
        response = self.client.get(reverse('databank:detail', kwargs={'pk': private_dataset.pk}))
        self.assertEqual(response.status_code, 403)

    def test_owner_can_edit_dataset(self):
        dataset = MarketData.objects.create(
            title='Original Title',
            company_name='Original Corp',
            category=self.category,
            industry='Tech',
            product_service='Software',
            market_price=Decimal('100.00'),
            market_demand='Medium',
            description='Desc',
            data_source='Source',
            collection_date=datetime.date.today(),
            visibility=MarketData.Visibility.PUBLIC,
            created_by=self.user
        )
        self.client.login(username='analyst1', password='Password123!')
        update_data = self.dataset_data.copy()
        update_data['title'] = 'Updated Title by Owner'
        response = self.client.post(reverse('databank:edit', kwargs={'pk': dataset.pk}), update_data)
        self.assertEqual(response.status_code, 302)
        dataset.refresh_from_db()
        self.assertEqual(dataset.title, 'Updated Title by Owner')

    def test_non_owner_cannot_edit_dataset(self):
        dataset = MarketData.objects.create(
            title='Original Title',
            company_name='Original Corp',
            category=self.category,
            industry='Tech',
            product_service='Software',
            market_price=Decimal('100.00'),
            market_demand='Medium',
            description='Desc',
            data_source='Source',
            collection_date=datetime.date.today(),
            visibility=MarketData.Visibility.PUBLIC,
            created_by=self.user
        )
        self.client.login(username='analyst2', password='Password123!')
        update_data = self.dataset_data.copy()
        update_data['title'] = 'Hacked Title'
        response = self.client.post(reverse('databank:edit', kwargs={'pk': dataset.pk}), update_data)
        self.assertEqual(response.status_code, 403)
        dataset.refresh_from_db()
        self.assertEqual(dataset.title, 'Original Title')

    def test_delete_dataset_owner_only(self):
        dataset = MarketData.objects.create(
            title='To be deleted',
            company_name='Delete Corp',
            category=self.category,
            industry='Tech',
            product_service='Software',
            market_price=Decimal('50.00'),
            market_demand='Low',
            description='Desc',
            data_source='Source',
            collection_date=datetime.date.today(),
            visibility=MarketData.Visibility.PUBLIC,
            created_by=self.user
        )
        # Other user tries to delete
        self.client.login(username='analyst2', password='Password123!')
        response = self.client.post(reverse('databank:delete', kwargs={'pk': dataset.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(MarketData.objects.filter(pk=dataset.pk).exists())

        # Owner deletes
        self.client.login(username='analyst1', password='Password123!')
        response = self.client.post(reverse('databank:delete', kwargs={'pk': dataset.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(MarketData.objects.filter(pk=dataset.pk).exists())

    def test_csv_export_and_sanitization(self):
        dataset = MarketData.objects.create(
            title='=SUM(A1:A10)',  # Potential formula injection
            company_name='@DangerousCompany',
            category=self.category,
            industry='Tech',
            product_service='Software, Tools & APIs',  # Commas inside field
            market_price=Decimal('100.00'),
            market_demand='High',
            description='Test description with special quotes "benchmark" and commas.',
            data_source='+SourceFormula',
            collection_date=datetime.date.today(),
            visibility=MarketData.Visibility.PUBLIC,
            created_by=self.user
        )
        self.client.login(username='analyst1', password='Password123!')
        response = self.client.get(reverse('databank:export_csv', kwargs={'pk': dataset.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        
        # Verify UTF-8 BOM is present at the start of binary stream
        self.assertTrue(response.content.startswith(b'\xef\xbb\xbf'))

        # Verify Content-Disposition filename
        self.assertIn('attachment; filename="MarketDatabank_', response['Content-Disposition'])

        content = response.content.decode('utf-8')

        # Verify 17 expected column headers
        expected_headers = "ID,Title,Company Name,Category,Industry,Product/Service,Market Price,Market Demand,Market Size,Growth Rate (%),Description,Data Source,Collection Date,Visibility,Creator,Created At,Updated At"
        self.assertIn(expected_headers, content)

        # Verify sanitization prepended apostrophe
        self.assertIn("'=SUM(A1:A10)", content)
        self.assertIn("'@DangerousCompany", content)
        self.assertIn("'+SourceFormula", content)

        # Verify comma escaping (wrapped in quotes)
        self.assertIn('"Software, Tools & APIs"', content)

    def test_csv_export_private_dataset_access_control(self):
        private_dataset = MarketData.objects.create(
            title='Confidential Strategy',
            company_name='Private Corp',
            category=self.category,
            industry='CleanTech',
            product_service='Batteries',
            market_price=Decimal('500.00'),
            market_demand='High',
            description='Proprietary cell study',
            data_source='Internal',
            collection_date=datetime.date.today(),
            visibility=MarketData.Visibility.PRIVATE,
            created_by=self.user
        )
        # Unauthorized user receives 403 Forbidden
        self.client.login(username='analyst2', password='Password123!')
        response = self.client.get(reverse('databank:export_csv', kwargs={'pk': private_dataset.pk}))
        self.assertEqual(response.status_code, 403)

        # Owner can download
        self.client.login(username='analyst1', password='Password123!')
        owner_response = self.client.get(reverse('databank:export_csv', kwargs={'pk': private_dataset.pk}))
        self.assertEqual(owner_response.status_code, 200)

    def test_pdf_export_authorized_and_valid_binary(self):
        dataset = MarketData.objects.create(
            title='EV Infrastructure Commercial Study',
            company_name='Tata Motors',
            category=self.category,
            industry='Automotive',
            product_service='Heavy Trucks',
            market_price=Decimal('2500000.00'),
            market_demand='High',
            market_size=Decimal('45000000.00'),
            market_growth_rate=Decimal('21.50'),
            description='In-depth research on commercial fleet electrification corridors.',
            data_source='Auto Ministry 2024 Report',
            collection_date=datetime.date.today(),
            visibility=MarketData.Visibility.PUBLIC,
            created_by=self.user
        )
        self.client.login(username='analyst1', password='Password123!')
        response = self.client.get(reverse('databank:export_pdf', kwargs={'pk': dataset.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # Verify valid PDF header
        self.assertTrue(response.content.startswith(b'%PDF-'))

        # Verify Content-Disposition filename
        self.assertIn('attachment; filename="MarketDatabank_', response['Content-Disposition'])
        self.assertIn('.pdf"', response['Content-Disposition'])

        # Verify activity log was recorded
        self.assertTrue(ActivityLog.objects.filter(dataset=dataset, action='Exported PDF').exists())

    def test_pdf_export_private_dataset_access_control(self):
        private_dataset = MarketData.objects.create(
            title='Private Drone Valuation',
            company_name='Defense Aero',
            category=self.category,
            industry='Aerospace',
            product_service='Surveillance UAV',
            market_price=Decimal('1200000.00'),
            market_demand='Medium',
            description='Proprietary aerodynamics study',
            data_source='Defense Lab',
            collection_date=datetime.date.today(),
            visibility=MarketData.Visibility.PRIVATE,
            created_by=self.user
        )
        # Unauthorized stranger receives 403 Forbidden
        self.client.login(username='analyst2', password='Password123!')
        response = self.client.get(reverse('databank:export_pdf', kwargs={'pk': private_dataset.pk}))
        self.assertEqual(response.status_code, 403)

        # Owner can download PDF
        self.client.login(username='analyst1', password='Password123!')
        owner_response = self.client.get(reverse('databank:export_pdf', kwargs={'pk': private_dataset.pk}))
        self.assertEqual(owner_response.status_code, 200)
        self.assertTrue(owner_response.content.startswith(b'%PDF-'))

    def test_pdf_export_collaborator_permissions(self):
        from sharing.models import DataShare
        private_dataset = MarketData.objects.create(
            title='Shared Research Report',
            company_name='Shared Corp',
            category=self.category,
            industry='FinTech',
            product_service='Payment Switch',
            market_price=Decimal('75000.00'),
            market_demand='High',
            description='Collaborative payments protocol analysis',
            data_source='Internal Consortium',
            collection_date=datetime.date.today(),
            visibility=MarketData.Visibility.PRIVATE,
            created_by=self.user
        )
        # Grant Viewer share to analyst2
        DataShare.objects.create(
            dataset=private_dataset,
            shared_by=self.user,
            shared_with=self.other_user,
            permission=DataShare.Permission.VIEWER,
            is_active=True
        )

        self.client.login(username='analyst2', password='Password123!')
        response = self.client.get(reverse('databank:export_pdf', kwargs={'pk': private_dataset.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b'%PDF-'))

    def test_sanitize_csv_cell_helper(self):
        self.assertEqual(sanitize_csv_cell('=1+1'), "'=1+1")
        self.assertEqual(sanitize_csv_cell('+cmd'), "'+cmd")
        self.assertEqual(sanitize_csv_cell('-cmd'), "'-cmd")
        self.assertEqual(sanitize_csv_cell('@calc'), "'@calc")
        self.assertEqual(sanitize_csv_cell('NormalText'), "NormalText")
        self.assertEqual(sanitize_csv_cell(123), "123")
