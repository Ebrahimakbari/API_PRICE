from django.test import TestCase
from django.utils import timezone
from assets.models import Asset, AssetPriceLog



class AssetModelTest(TestCase):
    """Test suite for the Asset model."""

    def setUp(self):
        self.asset = Asset.objects.create(
            symbol="gold_spot",
            name_fa="انس طلا",
            name_en="Gold Ounce",
            category="METAL"
        )

    def test_asset_creation(self):
        """Test that an Asset can be created correctly."""
        self.assertIsInstance(self.asset, Asset)
        self.assertEqual(self.asset.pk, "gold_spot")
        self.assertEqual(self.asset.__str__(), "انس طلا")

class AssetPriceLogModelTest(TestCase):
    """Test suite for the AssetPriceLog model."""

    def setUp(self):
        self.asset = Asset.objects.create(symbol="price_dollar_rl", name_fa="دلار")
        self.price_log = AssetPriceLog.objects.create(
            asset=self.asset,
            price=58500.00,
            high=58600.00,
            low=58400.00,
            change_amount=50.00,
            change_percent=0.09,
            timestamp=timezone.now()
        )

    def test_price_log_creation(self):
        """Test that a price log is correctly associated with an asset."""
        self.assertIsInstance(self.price_log, AssetPriceLog)
        self.assertEqual(self.price_log.asset, self.asset)
        self.assertEqual(self.asset.price_logs.count(), 1)
