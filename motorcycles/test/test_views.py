from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import MotorcycleBrand, Motorcycle


User = get_user_model()

class MotorcycleBrandAPITests(APITestCase):
    """Test suite for the MotorcycleBrand API endpoints."""
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', email='testuser@test.com', phone_number='09123456789', first_name='John', last_name='Doe')
        self.user.is_active = True
        self.user.save()
        self.admin_user = User.objects.create_superuser(username='admin', password='password123', email='admin@test.com', phone_number='09123416789', first_name='Admin', last_name='User')
        self.brand1 = MotorcycleBrand.objects.create(name_fa="سوزوکی", name_en_slug="suzuki")
        self.brand2 = MotorcycleBrand.objects.create(name_fa="یاماها", name_en_slug="yamaha")
        self.list_create_url = reverse('motorcycle-brand-list-create')
        self.detail_url = reverse('motorcycle-brand-detail', kwargs={'pk': self.brand1.pk})

    def test_anonymous_user_can_list_brands(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_brands(self):
        response = self.client.get(self.list_create_url, {'search': 'سوزوکی'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name_fa'], self.brand1.name_fa)

    def test_anonymous_user_cannot_create_brand(self):
        data = {'name_fa': 'دوکاتی', 'name_en_slug': 'ducati'}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create_brand(self):
        self.client.force_authenticate(user=self.user)
        data = {'name_fa': 'دوکاتی', 'name_en_slug': 'ducati'}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_create_brand(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name_fa': 'دوکاتی', 'name_en_slug': 'ducati'}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MotorcycleBrand.objects.count(), 3)

    def test_admin_can_update_brand(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name_fa': 'سوزوکی ژاپن', 'name_en_slug': 'suzuki-jp'}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.brand1.refresh_from_db()
        self.assertEqual(self.brand1.name_fa, 'سوزوکی ژاپن')

    def test_regular_user_cannot_delete_brand(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_brand(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MotorcycleBrand.objects.count(), 1)


class MotorcycleAPITests(APITestCase):
    """Test suite for the Motorcycle API endpoints."""
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', email='testuser@test.com', phone_number='09123456789', first_name='John', last_name='Doe')
        self.user.is_active = True
        self.user.save()
        self.admin_user = User.objects.create_superuser(username='admin', password='password123', email='admin@test.com', phone_number='09123416789', first_name='Admin', last_name='User')
        self.brand = MotorcycleBrand.objects.create(name_fa="بنلی", name_en_slug="benelli")
        self.motorcycle = Motorcycle.objects.create(
            brand=self.brand,
            model_fa="TNT25N",
            model_en_slug="tnt25n",
            trim_fa="تک سیلندر",
            production_year=1401
        )
        self.list_create_url = reverse('motorcycle-list-create')
        self.detail_url = reverse('motorcycle-detail', kwargs={'pk': self.motorcycle.pk})

    def test_anonymous_user_can_list_motorcycles(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['brand']['name_fa'], self.brand.name_fa)

    def test_search_motorcycles(self):
        response = self.client.get(self.list_create_url, {'search': 'tnt'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_create_motorcycle(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "brand": self.brand.pk,
            "model_fa": "S302",
            "model_en_slug": "s302",
            "trim_fa": "دو سیلندر",
            "production_year": 1403,
            "origin": "Italy/China"
        }
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Motorcycle.objects.count(), 2)
        self.assertEqual(response.data['brand']['name_fa'], self.brand.name_fa)

    def test_regular_user_cannot_create_motorcycle(self):
        self.client.force_authenticate(user=self.user)
        data = {"brand": self.brand.pk, "model_fa": "S302"}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_motorcycle(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "brand": self.brand.pk,
            "model_fa": "TNT249N",
            "model_en_slug": "tnt25n",
            "trim_fa": "تک سیلندر",
            "production_year": 1401
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.motorcycle.refresh_from_db()
        self.assertEqual(self.motorcycle.model_fa, "TNT249N")

    def test_admin_can_delete_motorcycle(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Motorcycle.objects.filter(pk=self.motorcycle.pk).exists())