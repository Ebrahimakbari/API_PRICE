from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from cars.models import Brand, Vehicle


User = get_user_model()



class BrandAPITests(APITestCase):
    """Test suite for the Brand API endpoints."""
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', email='testuser@test.com', phone_number='09123456789', first_name='John', last_name='Doe')
        self.user.is_active = True
        self.user.save()
        self.admin_user = User.objects.create_superuser(username='admin', password='password123', email='admin@test.com', phone_number='09123416789', first_name='Admin', last_name='User')
        self.brand1 = Brand.objects.create(name_fa="ایران خودرو", name_en="Iran Khodro")
        self.brand2 = Brand.objects.create(name_fa="سایپا", name_en="Saipa")
        self.list_create_url = reverse('brand-list-create')
        self.detail_url = reverse('brand-detail', kwargs={'pk': self.brand1.pk})

    def test_anonymous_user_can_list_brands(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_brands(self):
        response = self.client.get(self.list_create_url, {'search': 'ایران'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name_fa'], self.brand1.name_fa)

    def test_anonymous_user_cannot_create_brand(self):
        data = {'name_fa': 'مدیران خودرو', 'name_en': 'MVM'}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create_brand(self):
        self.client.force_authenticate(user=self.user)
        data = {'name_fa': 'مدیران خودرو', 'name_en': 'MVM'}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_create_brand(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name_fa': 'مدیران خودرو', 'name_en': 'MVM'}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Brand.objects.count(), 3)

    def test_admin_can_update_brand(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name_fa': 'ایران خودرو جدید', 'name_en': 'New IKCO'}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.brand1.refresh_from_db()
        self.assertEqual(self.brand1.name_fa, 'ایران خودرو جدید')

    def test_regular_user_cannot_delete_brand(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_brand(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Brand.objects.count(), 1)


class VehicleAPITests(APITestCase):
    """Test suite for the Vehicle API endpoints."""
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', email='testuser@est.com', phone_number='09123456781', first_name='John', last_name='Doe')
        self.user.is_active = True
        self.user.save()
        self.admin_user = User.objects.create_superuser(username='admin', password='password123', email='admin@tes.com', phone_number='09123456782', first_name='Admin', last_name='User')
        self.brand = Brand.objects.create(name_fa="پژو", name_en="Peugeot")
        self.vehicle = Vehicle.objects.create(
            brand=self.brand,
            model_fa="پارس",
            model_en="Pars",
            trim_fa="LX",
            production_year=1402
        )
        self.list_create_url = reverse('vehicle-list-create')
        self.detail_url = reverse('vehicle-detail', kwargs={'pk': self.vehicle.pk})

    def test_anonymous_user_can_list_vehicles(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['brand']['name_fa'], self.brand.name_fa)

    def test_search_vehicles(self):
        response = self.client.get(self.list_create_url, {'search': 'پارس'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_create_vehicle(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "brand": self.brand.pk,
            "model_fa": "207",
            "model_en": "207i",
            "trim_fa": "پانوراما", # This was missing
            "production_year": 1403,
            "specifications_fa": "موتور 1.6 لیتری",
            "specifications_en": "1.6L engine"
        }
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Vehicle.objects.count(), 2)
        self.assertEqual(response.data['brand']['name_fa'], self.brand.name_fa)

    def test_regular_user_cannot_create_vehicle(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "brand": self.brand.pk, 
            "model_fa": "207", 
            "trim_fa": "معمولی", # Also add here to be safe
            "production_year": 1403,
            "specifications_fa": "موتور 1.6 لیتری",
            "specifications_en": "1.6L engine"
        }
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_vehicle(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "brand": self.brand.pk,
            "model_fa": "پارس سال",
            "model_en": "Pars Sal",
            "trim_fa": "ELX", # This was present, but good to confirm
            "production_year": 1402,
            "specifications_fa": "موتور 1.6 لیتری",
            "specifications_en": "1.6L engine"
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.model_fa, "پارس سال")

    def test_admin_can_delete_vehicle(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Vehicle.objects.filter(pk=self.vehicle.pk).exists())
