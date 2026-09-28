from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Lead, LeadActivity

User = get_user_model()


class LeadAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testagent', password='testpassword123', email='agent@crm.test')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.lead1 = Lead.objects.create(
            name='Alisher Usmanov',
            phone='+998901112233',
            email='alisher@example.com',
            source='telegram',
            status=Lead.StatusChoices.NEW,
            note='Initial inquiry regarding CRM deployment',
            assigned_to=self.user
        )
        self.lead2 = Lead.objects.create(
            name='Bekzod Mirzayev',
            phone='+998912223344',
            email='bekzod@partner.uz',
            source='website',
            status=Lead.StatusChoices.QUALIFIED,
            note='Interested in annual contract'
        )

    def test_authentication_required(self):
        unauth_client = APIClient()
        response = unauth_client.get(reverse('lead-list'))
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_list_leads_and_pagination(self):
        response = self.client.get(reverse('lead-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIn('results', response.data)
        self.assertIn('total_pages', response.data)

    def test_create_lead_success(self):
        payload = {
            'name': 'Dilorom Karimova',
            'phone': '+998933334455',
            'email': 'dilorom@business.uz',
            'source': 'referral',
            'status': 'new',
            'note': 'Referred by Bekzod'
        }
        response = self.client.post(reverse('lead-list'), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Dilorom Karimova')
        
        # Verify activity was recorded
        lead_id = response.data['id']
        lead = Lead.objects.get(id=lead_id)
        self.assertTrue(lead.activities.filter(action='CREATED').exists())

    def test_create_lead_validation_missing_name_and_source(self):
        payload = {
            'phone': '+998901234567'
        }
        response = self.client.post(reverse('lead-list'), payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('source', response.data)

    def test_retrieve_lead_detail(self):
        response = self.client.get(reverse('lead-detail', kwargs={'pk': self.lead1.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.lead1.name)
        self.assertEqual(response.data['source'], 'telegram')

    def test_update_lead_and_status_change_creates_activity(self):
        url = reverse('lead-detail', kwargs={'pk': self.lead1.pk})
        # Change status from NEW to CONTACTED
        response = self.client.patch(url, {'status': 'contacted'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'contacted')

        activities = self.lead1.activities.filter(action='STATUS_CHANGE')
        self.assertTrue(activities.exists())
        latest = activities.latest('created_at')
        self.assertEqual(latest.old_status, 'new')
        self.assertEqual(latest.new_status, 'contacted')

    def test_lead_activities_endpoint(self):
        url = reverse('lead-activities', kwargs={'pk': self.lead1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_delete_lead(self):
        url = reverse('lead-detail', kwargs={'pk': self.lead2.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lead.objects.filter(pk=self.lead2.pk).exists())

    def test_filtering_by_status_and_source(self):
        # Filter by status=new
        res1 = self.client.get(reverse('lead-list') + '?status=new')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res1.data['count'], 1)
        self.assertEqual(res1.data['results'][0]['name'], 'Alisher Usmanov')

        # Filter by source=website
        res2 = self.client.get(reverse('lead-list') + '?source=website')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data['count'], 1)
        self.assertEqual(res2.data['results'][0]['name'], 'Bekzod Mirzayev')

        # Combined filter
        res3 = self.client.get(reverse('lead-list') + '?status=qualified&source=website')
        self.assertEqual(res3.status_code, status.HTTP_200_OK)
        self.assertEqual(res3.data['count'], 1)

    def test_search(self):
        response = self.client.get(reverse('lead-list') + '?search=alisher')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Alisher Usmanov')

    def test_dashboard_stats_api(self):
        url = reverse('dashboard-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 2)
        self.assertEqual(response.data['new'], 1)
        self.assertEqual(response.data['qualified'], 1)
        self.assertEqual(response.data['won'], 0)
