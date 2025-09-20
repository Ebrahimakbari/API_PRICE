from django.test import TestCase
from django.db.utils import IntegrityError
from motorcycles.models import MotorcycleBrand, Motorcycle




class MotorcycleBrandModelTest(TestCase):
    """Test suite for the MotorcycleBrand model."""

    def setUp(self):
        self.brand = MotorcycleBrand.objects.create(name_fa="یاماها", name_en_slug="yamaha")

    def test_brand_creation(self):
        """Test that a MotorcycleBrand can be created."""
        self.assertIsInstance(self.brand, MotorcycleBrand)
        self.assertEqual(self.brand.__str__(), "یاماها (yamaha)")

    def test_brand_name_uniqueness_violation(self):
        """Test that creating a brand with duplicate name raises IntegrityError."""
        with self.assertRaises(IntegrityError):
            MotorcycleBrand.objects.create(name_fa="یاماها", name_en_slug="yamaha-test")

    def test_brand_name_uniqueness_success(self):
        """Test that creating a brand with unique name succeeds."""
        new_brand = MotorcycleBrand.objects.create(
            name_fa="کاوازاکی", 
            name_en_slug="kawasaki"
        )
        self.assertEqual(new_brand.name_fa, "کاوازاکی")


class MotorcycleModelTest(TestCase):
    """Test suite for the Motorcycle model."""

    def setUp(self):
        self.brand = MotorcycleBrand.objects.create(name_fa="بنلی", name_en_slug="benelli")
        self.motorcycle = Motorcycle.objects.create(
            brand=self.brand,
            model_fa="302S",
            trim_fa="دو سیلندر",
            production_year=1402,
            origin="Italy"
        )

    def test_motorcycle_creation(self):
        """Test that a Motorcycle can be created with its brand."""
        self.assertIsInstance(self.motorcycle, Motorcycle)
        self.assertEqual(self.motorcycle.brand.name_fa, "بنلی")
        self.assertEqual(self.motorcycle.__str__(), "بنلی 302S دو سیلندر (1402)")

    def test_motorcycle_uniqueness_constraint(self):
        """Test that the same motorcycle variant cannot be created twice."""
        with self.assertRaises(IntegrityError):
            Motorcycle.objects.create(
                brand=self.brand,
                model_fa="302S",
                trim_fa="دو سیلندر",
                production_year=1402
            )
