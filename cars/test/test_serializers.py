from django.test import TestCase
from cars.models import Brand, Vehicle
from cars.serializers import BrandSerializer, VehicleSerializer, VehicleWriteSerializer






class BrandSerializerTest(TestCase):
    """Test suite for the BrandSerializer."""

    def setUp(self):
        self.brand = Brand.objects.create(name_fa="سایپا", name_en="Saipa")
        self.serializer = BrandSerializer(instance=self.brand)

    def test_brand_serializer_contains_expected_fields(self):
        """Ensure the serializer output has the correct fields."""
        data = self.serializer.data
        self.assertEqual(set(data.keys()), {'id', 'name_fa', 'name_en'})
        self.assertEqual(data['name_fa'], "سایپا")


class VehicleSerializerTest(TestCase):
    """Test suite for the Vehicle serializers."""

    def setUp(self):
        self.brand = Brand.objects.create(name_fa="پژو", name_en="Peugeot")
        self.vehicle_attributes = {
            "brand": self.brand,
            "model_fa": "207", "model_en": "207i",
            "trim_fa": "پانوراما", "trim_en": "Panorama",
            "production_year": 1403,
            "specifications_fa": "فول", "specifications_en": "Full"
        }
        self.vehicle = Vehicle.objects.create(**self.vehicle_attributes)
    
    def test_vehicle_read_serializer(self):
        """Test the read-only VehicleSerializer for nested data."""
        serializer = VehicleSerializer(instance=self.vehicle)
        data = serializer.data
        self.assertEqual(set(data.keys()), {
            'id', 'brand', 'model_fa', 'model_en', 'trim_fa', 'trim_en', 
            'production_year', 'specifications_fa', 'specifications_en', 'price_logs'
        })
        self.assertEqual(data['brand']['name_fa'], "پژو")

    def test_vehicle_write_serializer_valid_data(self):
        """Test the write serializer with valid data."""
        valid_serializer_data = {
            "brand": self.brand.pk,
            "model_fa": "دنا",
            "trim_fa": "پلاس", # This field was missing
            "production_year": 1404,
            "specifications_fa": "فول",
            "specifications_en": "Full"
            
        }
        serializer = VehicleWriteSerializer(data=valid_serializer_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIn('brand', serializer.validated_data)

    def test_vehicle_write_serializer_invalid_data(self):
        """Test the write serializer with missing required fields."""
        invalid_serializer_data = {
            "brand": self.brand.pk,
        }
        serializer = VehicleWriteSerializer(data=invalid_serializer_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('model_fa', serializer.errors)
