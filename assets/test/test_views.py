from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assets.models import Asset


User = get_user_model()

class AssetAPITests(APITestCase):
    """
    Test suite for the Asset API endpoints.
    """

    def setUp(self):
        """Set up initial data and users for the tests."""
        # Users
        self.user = User.objects.create_user(username='testuser', password='password123', email='testuser@test.com', phone_number='09123456789', first_name='John', last_name='Doe')
        self.user.is_active = True
        self.user.save()
        self.admin_user = User.objects.create_superuser(username='admin', password='password123', email='admin@test.com', phone_number='09123416789', first_name='Admin', last_name='User')
        # Data
        self.asset1 = Asset.objects.create(symbol="gold_spot", name_fa="انس طلا", name_en="Gold Ounce", category="METAL")
        self.asset2 = Asset.objects.create(symbol="price_dollar_rl", name_fa="دلار آمریکا", name_en="US Dollar", category="CURRENCY")
        
        # URLs
        self.list_create_url = reverse('asset-list-create')
        self.detail_url = reverse('asset-detail', kwargs={'pk': self.asset1.pk}) # pk is the symbol

    # --- LIST / SEARCH / FILTER (GET) Tests ---
    def test_anonymous_user_can_list_assets(self):
        """Ensure any user can list all assets."""
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_assets(self):
        """Ensure asset search works on symbol, name_fa, and name_en."""
        response = self.client.get(self.list_create_url, {'search': 'طلا'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['symbol'], self.asset1.symbol)

    def test_filter_assets_by_category(self):
        """Ensure filtering by category works correctly."""
        response = self.client.get(self.list_create_url, {'category': 'CURRENCY'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['symbol'], self.asset2.symbol)

    # --- CREATE (POST) Tests ---
    def test_regular_user_cannot_create_asset(self):
        """Ensure regular users are forbidden from creating an asset."""
        self.client.force_authenticate(user=self.user)
        data = {'symbol': 'oil_brent', 'name_fa': 'نفت برنت', 'category': 'COMMODITY'}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_create_asset(self):
        """Ensure admin users can successfully create a new asset."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'symbol': 'oil_brent', 'name_fa': 'نفت برنت', 'category': 'COMMODITY'}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Asset.objects.count(), 3)
        self.assertEqual(response.data['name_fa'], 'نفت برنت')

    # --- RETRIEVE / UPDATE / DELETE Tests ---
    def test_admin_can_update_asset(self):
        """Ensure an admin can update an existing asset."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'symbol': 'gold_spot', 'name_fa': 'طلای جهانی', 'name_en': 'Global Gold', 'category': 'METAL'}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.asset1.refresh_from_db()
        self.assertEqual(self.asset1.name_fa, 'طلای جهانی')

    def test_admin_can_delete_asset(self):
        """Ensure an admin can delete an asset."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Asset.objects.count(), 1)
