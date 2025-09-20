from django.test import TestCase
from motorcycles.models import MotorcycleBrand, Motorcycle, MotorcyclePriceLog
from motorcycles.serializers import MotorcycleBrandSerializer, MotorcycleSerializer, MotorcycleWriteSerializer





class MotorcycleBrandSerializerTest(TestCase):
    """Test suite for the MotorcycleBrandSerializer."""

    def setUp(self):
        self.brand = MotorcycleBrand.objects.create(name_fa="هوندا", name_en_slug="honda")
        self.serializer = MotorcycleBrandSerializer(instance=self.brand)

    def test_brand_serializer_contains_expected_fields(self):
        """Ensure the serializer output has the correct fields."""
        data = self.serializer.data
        self.assertEqual(set(data.keys()), {'id', 'name_fa', 'name_en_slug'})
        self.assertEqual(data['name_fa'], "هوندا")


class MotorcycleSerializerTest(TestCase):
    """Test suite for the Motorcycle serializers."""

    def setUp(self):
        self.brand = MotorcycleBrand.objects.create(name_fa="کاوازاکی", name_en_slug="kawasaki")
        self.motorcycle = Motorcycle.objects.create(
            brand=self.brand,
            model_fa="Ninja H2",
            model_en_slug="ninja-h2",
            trim_fa="Carbon",
            production_year=2024,
            origin="Japan"
        )
        MotorcyclePriceLog.objects.create(motorcycle=self.motorcycle, price=1000000000, source="Bama")

    def test_motorcycle_read_serializer(self):
        """Test the read-only MotorcycleSerializer for nested data."""
        serializer = MotorcycleSerializer(instance=self.motorcycle)
        data = serializer.data
        self.assertEqual(set(data.keys()), {
            'id', 'brand', 'model_fa', 'model_en_slug', 'trim_fa', 
            'production_year', 'origin', 'price_logs'
        })
        self.assertEqual(data['brand']['name_fa'], "کاوازاکی")
        self.assertEqual(len(data['price_logs']), 1)
        self.assertEqual(data['price_logs'][0]['price'], 1000000000)

    def test_motorcycle_write_serializer_valid_data(self):
        """Test the write serializer with valid data."""
        valid_serializer_data = {
            "brand": self.brand.pk,
            "model_fa": "Z1000",
            "production_year": 2023,
            "origin": "Japan"
        }
        serializer = MotorcycleWriteSerializer(data=valid_serializer_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIn('brand', serializer.validated_data)

    def test_motorcycle_write_serializer_invalid_data(self):
        """Test the write serializer with missing required fields."""
        invalid_serializer_data = {
            "brand": self.brand.pk,
            "origin": "Japan"
        }
        serializer = MotorcycleWriteSerializer(data=invalid_serializer_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('model_fa', serializer.errors)