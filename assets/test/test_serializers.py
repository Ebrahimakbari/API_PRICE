from django.test import TestCase
from django.utils import timezone
from assets.models import Asset, AssetPriceLog
from assets.serializers import AssetSerializer, AssetWriteSerializer




class AssetSerializerTest(TestCase):
    """Test suite for the Asset serializers."""

    def setUp(self):
        self.asset = Asset.objects.create(
            symbol="silver",
            name_fa="نقره",
            name_en="Silver",
            category="METAL"
        )
        # Create a price log to test the 'latest_price' field
        self.price_log = AssetPriceLog.objects.create(
            asset=self.asset,
            price=43.11, high=43.11, low=42.93,
            change_amount=0.14, change_percent=0.32,
            timestamp=timezone.now()
        )
    
    def test_asset_read_serializer(self):
        """Test the read-only AssetSerializer for correct fields and nested data."""
        serializer = AssetSerializer(instance=self.asset)
        data = serializer.data
        
        self.assertEqual(set(data.keys()), {'symbol', 'name_fa', 'name_en', 'category', 'latest_price'})
        self.assertIsNotNone(data['latest_price'])
        self.assertEqual(float(data['latest_price']['price']), 43.11)

    def test_asset_write_serializer_valid_data(self):
        """Test the write serializer with valid data."""
        valid_data = {
            "symbol": "price_eur",
            "name_fa": "یورو",
            "name_en": "Euro",
            "category": "CURRENCY"
        }
        serializer = AssetWriteSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        asset = serializer.save()
        self.assertEqual(asset.name_fa, "یورو")

    def test_asset_write_serializer_invalid_data(self):
        """Test the write serializer with a missing required field (symbol)."""
        invalid_data = {
            "name_fa": "نفت برنت",
            "category": "COMMODITY"
        }
        serializer = AssetWriteSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('symbol', serializer.errors)
