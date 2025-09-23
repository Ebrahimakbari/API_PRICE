from rest_framework import serializers
from .models import Asset, AssetPriceLog




class AssetPriceLogSerializer(serializers.ModelSerializer):
    """Serializer for a single price log entry."""
    class Meta:
        model = AssetPriceLog
        fields = [
            'price', 'high', 'low', 
            'change_amount', 'change_percent', 'timestamp'
        ]


class AssetSerializer(serializers.ModelSerializer):
    """
    READ-ONLY serializer for the Asset model.
    Includes a custom field to display only the latest price log.
    """
    # This field will dynamically get the latest price for each asset.
    latest_price = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = ['symbol', 'name_fa', 'name_en', 'category', 'latest_price']

    def get_latest_price(self, obj):
        """
        Retrieves the most recent price log for the asset.
        """
        latest_log = obj.price_logs.first()
        if latest_log:
            # Reuse the PriceLog serializer to format the data
            return AssetPriceLogSerializer(latest_log).data
        return None


class AssetWriteSerializer(serializers.ModelSerializer):
    """WRITE-ONLY serializer for creating and updating Assets."""
    class Meta:
        model = Asset
        fields = ['symbol', 'name_fa', 'name_en', 'category']


class AssetPriceLogSerializer(serializers.ModelSerializer):
    """
    Serializer for a single record of price history.
    """
    class Meta:
        model = AssetPriceLog
        # These fields are perfect for a chart
        fields = ['price', 'high', 'low', 'timestamp']
        read_only_fields = fields
