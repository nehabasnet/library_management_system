from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date, timedelta
from .models import Category, Book, Student, IssueBook

class DashboardAccessTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='staff', password='testpass123')

    def test_dashboard_redirects_when_not_logged_in(self):
        response = self.client.get(reverse('dashboard'))
        self.assertNotEqual(response.status_code, 200)  # should redirect to login

    def test_dashboard_loads_when_logged_in(self):
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)


