import datetime
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from databank.models import Category, MarketData
from sharing.models import DataShare

class DatasetSharingPermissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='dataset_owner', password='Password123!')
        self.collab_viewer = User.objects.create_user(username='collab_viewer', password='Password123!')
        self.collab_editor = User.objects.create_user(username='collab_editor', password='Password123!')
        self.stranger = User.objects.create_user(username='stranger', password='Password123!')

        self.category = Category.objects.create(name='IT', description='Technology')

        self.private_dataset = MarketData.objects.create(
            title='Confidential Fintech Roadmap',
            company_name='Fintech Labs',
            category=self.category,
            industry='Fintech',
            product_service='Payment Gateway Core',
            market_price=Decimal('75000.00'),
            market_demand='High',
            description='Proprietary payment protocols and partner commissions.',
            data_source='Internal Strategic Planning 2025',
            collection_date=datetime.date.today(),
            visibility=MarketData.Visibility.PRIVATE,
            created_by=self.owner
        )

    def test_share_dataset_success(self):
        self.client.login(username='dataset_owner', password='Password123!')
        response = self.client.post(
            reverse('sharing:share_dataset', kwargs={'dataset_id': self.private_dataset.pk}),
            {
                'recipient_identifier': 'collab_viewer',
                'permission': DataShare.Permission.VIEWER,
                'message': 'Here is the private market brief.'
            }
        )
        self.assertEqual(response.status_code, 302)
        share = DataShare.objects.get(dataset=self.private_dataset, shared_with=self.collab_viewer)
        self.assertEqual(share.permission, DataShare.Permission.VIEWER)
        self.assertTrue(share.is_active)

    def test_prevent_share_with_self(self):
        self.client.login(username='dataset_owner', password='Password123!')
        response = self.client.post(
            reverse('sharing:share_dataset', kwargs={'dataset_id': self.private_dataset.pk}),
            {
                'recipient_identifier': 'dataset_owner',
                'permission': DataShare.Permission.VIEWER,
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cannot share a dataset with yourself")

    def test_prevent_duplicate_share(self):
        DataShare.objects.create(
            dataset=self.private_dataset,
            shared_by=self.owner,
            shared_with=self.collab_viewer,
            permission=DataShare.Permission.VIEWER
        )
        self.client.login(username='dataset_owner', password='Password123!')
        response = self.client.post(
            reverse('sharing:share_dataset', kwargs={'dataset_id': self.private_dataset.pk}),
            {
                'recipient_identifier': 'collab_viewer',
                'permission': DataShare.Permission.EDITOR,
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already actively shared")

    def test_viewer_permission_can_view_and_download_but_cannot_edit(self):
        DataShare.objects.create(
            dataset=self.private_dataset,
            shared_by=self.owner,
            shared_with=self.collab_viewer,
            permission=DataShare.Permission.VIEWER
        )

        self.client.login(username='collab_viewer', password='Password123!')
        
        # 1. Can view
        detail_res = self.client.get(reverse('databank:detail', kwargs={'pk': self.private_dataset.pk}))
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, 'Confidential Fintech Roadmap')

        # 2. Can download CSV
        csv_res = self.client.get(reverse('databank:export_csv', kwargs={'pk': self.private_dataset.pk}))
        self.assertEqual(csv_res.status_code, 200)

        # 3. Cannot edit (forbidden 403)
        edit_res = self.client.post(
            reverse('databank:edit', kwargs={'pk': self.private_dataset.pk}),
            {'title': 'Tampered by Viewer'}
        )
        self.assertEqual(edit_res.status_code, 403)

    def test_editor_permission_can_edit(self):
        DataShare.objects.create(
            dataset=self.private_dataset,
            shared_by=self.owner,
            shared_with=self.collab_editor,
            permission=DataShare.Permission.EDITOR
        )

        self.client.login(username='collab_editor', password='Password123!')
        edit_data = {
            'title': 'Fintech Roadmap - Updated by Editor',
            'company_name': 'Fintech Labs',
            'category': self.category.id,
            'industry': 'Fintech',
            'product_service': 'Payment Gateway Core',
            'market_price': '80000.00',
            'market_demand': 'High',
            'description': 'Updated description by editor',
            'data_source': 'Strategic update',
            'collection_date': datetime.date.today().strftime('%Y-%m-%d'),
            'visibility': 'Private',
        }
        edit_res = self.client.post(
            reverse('databank:edit', kwargs={'pk': self.private_dataset.pk}),
            edit_data
        )
        self.assertEqual(edit_res.status_code, 302)
        self.private_dataset.refresh_from_db()
        self.assertEqual(self.private_dataset.title, 'Fintech Roadmap - Updated by Editor')
        # Creator should still be original owner
        self.assertEqual(self.private_dataset.created_by, self.owner)

    def test_revoking_share_denies_subsequent_access(self):
        share = DataShare.objects.create(
            dataset=self.private_dataset,
            shared_by=self.owner,
            shared_with=self.collab_viewer,
            permission=DataShare.Permission.VIEWER
        )

        # Owner revokes
        self.client.login(username='dataset_owner', password='Password123!')
        revoke_res = self.client.post(reverse('sharing:revoke_share', kwargs={'share_id': share.pk}))
        self.assertEqual(revoke_res.status_code, 302)

        share.refresh_from_db()
        self.assertFalse(share.is_active)

        # Ex-collaborator attempts to view private dataset -> forbidden (403)
        self.client.login(username='collab_viewer', password='Password123!')
        detail_res = self.client.get(reverse('databank:detail', kwargs={'pk': self.private_dataset.pk}))
        self.assertEqual(detail_res.status_code, 403)

    def test_update_share_permission_by_owner(self):
        share = DataShare.objects.create(
            dataset=self.private_dataset,
            shared_by=self.owner,
            shared_with=self.collab_viewer,
            permission=DataShare.Permission.VIEWER
        )

        self.client.login(username='dataset_owner', password='Password123!')
        response = self.client.post(
            reverse('sharing:update_share', kwargs={'share_id': share.pk}),
            {'permission': DataShare.Permission.EDITOR}
        )
        self.assertEqual(response.status_code, 302)
        share.refresh_from_db()
        self.assertEqual(share.permission, DataShare.Permission.EDITOR)

    def test_update_share_permission_forbidden_to_non_owner(self):
        share = DataShare.objects.create(
            dataset=self.private_dataset,
            shared_by=self.owner,
            shared_with=self.collab_viewer,
            permission=DataShare.Permission.VIEWER
        )

        self.client.login(username='stranger', password='Password123!')
        response = self.client.post(
            reverse('sharing:update_share', kwargs={'share_id': share.pk}),
            {'permission': DataShare.Permission.EDITOR}
        )
        self.assertEqual(response.status_code, 403)
        share.refresh_from_db()
        self.assertEqual(share.permission, DataShare.Permission.VIEWER)

    def test_reshare_reactivates_revoked_share(self):
        share = DataShare.objects.create(
            dataset=self.private_dataset,
            shared_by=self.owner,
            shared_with=self.collab_viewer,
            permission=DataShare.Permission.VIEWER,
            is_active=False
        )

        self.client.login(username='dataset_owner', password='Password123!')
        response = self.client.post(
            reverse('sharing:share_dataset', kwargs={'dataset_id': self.private_dataset.pk}),
            {
                'recipient_identifier': 'collab_viewer',
                'permission': DataShare.Permission.EDITOR,
                'message': 'Welcome back as editor'
            }
        )
        self.assertEqual(response.status_code, 302)
        share.refresh_from_db()
        self.assertTrue(share.is_active)
        self.assertEqual(share.permission, DataShare.Permission.EDITOR)
        self.assertEqual(share.message, 'Welcome back as editor')

    def test_safe_redirect_prevents_open_redirect_on_update_and_revoke(self):
        share = DataShare.objects.create(
            dataset=self.private_dataset,
            shared_by=self.owner,
            shared_with=self.collab_viewer,
            permission=DataShare.Permission.VIEWER
        )

        self.client.login(username='dataset_owner', password='Password123!')

        # Malicious external URL in next parameter during update
        update_res = self.client.post(
            reverse('sharing:update_share', kwargs={'share_id': share.pk}),
            {
                'permission': DataShare.Permission.EDITOR,
                'next': 'https://evil-phishing-site.com/steal'
            }
        )
        self.assertEqual(update_res.status_code, 302)
        # Must redirect safely to internal dataset details, not evil external site
        self.assertEqual(update_res.url, reverse('databank:detail', kwargs={'pk': self.private_dataset.pk}))

        # Malicious external URL in next parameter during revoke
        revoke_res = self.client.post(
            reverse('sharing:revoke_share', kwargs={'share_id': share.pk}),
            {
                'next': 'https://evil-phishing-site.com/steal'
            }
        )
        self.assertEqual(revoke_res.status_code, 302)
        # Must redirect safely to internal dataset details, not evil external site
        self.assertEqual(revoke_res.url, reverse('databank:detail', kwargs={'pk': self.private_dataset.pk}))
