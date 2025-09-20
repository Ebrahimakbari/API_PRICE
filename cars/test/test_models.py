from django.test import TestCase
from cars.models import Brand, Vehicle





class BrandModelTest(TestCase):
    """Test suite for the Brand model."""

    def setUp(self):
        self.brand = Brand.objects.create(name_fa="ایران خودرو", name_en="Iran Khodro")

    def test_brand_creation(self):
        """Test that a Brand can be created."""
        self.assertIsInstance(self.brand, Brand)
        self.assertEqual(self.brand.__str__(), "ایران خودرو (Iran Khodro)")

class VehicleModelTest(TestCase):
    """Test suite for the Vehicle model."""

    def setUp(self):
        self.brand = Brand.objects.create(name_fa="پژو", name_en="Peugeot")
        self.vehicle = Vehicle.objects.create(
            brand=self.brand,
            model_fa="پارس",
            model_en="Pars",
            trim_fa="LX",
            production_year=1402
        )

    def test_vehicle_creation(self):
        """Test that a Vehicle can be created with its brand."""
        self.assertIsInstance(self.vehicle, Vehicle)
        self.assertEqual(self.vehicle.brand.name_fa, "پژو")
        self.assertEqual(self.vehicle.__str__(), "پژو پارس - LX (1402)")
