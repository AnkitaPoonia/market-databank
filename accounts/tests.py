from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class AccountsAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')
        self.profile_url = reverse('accounts:profile')
        self.dashboard_url = reverse('databank:dashboard')

        self.user_data = {
            'username': 'researcher1',
            'email': 'researcher1@example.com',
            'password': 'ComplexPassword123!',
            'confirm_password': 'ComplexPassword123!',
        }

    def test_user_registration_success(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        self.assertTrue(User.objects.filter(username='researcher1').exists())

    def test_user_registration_password_mismatch(self):
        bad_data = self.user_data.copy()
        bad_data['confirm_password'] = 'DifferentPassword456!'
        response = self.client.post(self.register_url, bad_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'confirm_password', 'Passwords do not match.')

    def test_user_registration_duplicate_username(self):
        User.objects.create_user(username='researcher1', email='old@example.com', password='password123')
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='researcher1@example.com').exists())

    def test_user_login_success(self):
        User.objects.create_user(username='researcher1', email='r@example.com', password='ComplexPassword123!')
        response = self.client.post(self.login_url, {
            'username': 'researcher1',
            'password': 'ComplexPassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.dashboard_url)

    def test_user_login_invalid_credentials(self):
        User.objects.create_user(username='researcher1', email='r@example.com', password='ComplexPassword123!')
        response = self.client.post(self.login_url, {
            'username': 'researcher1',
            'password': 'WrongPassword999'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

    def test_unauthorized_dashboard_access_redirects(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))

    def test_user_logout(self):
        user = User.objects.create_user(username='researcher1', password='ComplexPassword123!')
        self.client.login(username='researcher1', password='ComplexPassword123!')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)

    def test_profile_update(self):
        user = User.objects.create_user(username='researcher1', email='old@example.com', password='ComplexPassword123!')
        self.client.login(username='researcher1', password='ComplexPassword123!')
        response = self.client.post(self.profile_url, {
            'first_name': 'Anita',
            'last_name': 'Sharma',
            'email': 'new_email@example.com',
        })
        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Anita')
        self.assertEqual(user.email, 'new_email@example.com')
