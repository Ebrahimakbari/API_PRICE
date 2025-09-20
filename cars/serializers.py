from rest_framework import serializers
from .models import Brand, Vehicle, PriceLog




class PriceLogSerializer(serializers.ModelSerializer):
    """Serializer for price history, nested inside the Vehicle serializer."""
    class Meta:
        model = PriceLog
        fields = ['price', 'log_date']
        read_only_fields = fields


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for the Brand model, exposing both languages."""
    class Meta:
        model = Brand
        fields = ['id', 'name_fa', 'name_en']


class VehicleSerializer(serializers.ModelSerializer):
    """
    READ-ONLY serializer for the Vehicle model.
    Displays rich, nested output with all multilingual fields.
    """
    brand = BrandSerializer(read_only=True)
    price_logs = PriceLogSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        # Expose all new Persian and English fields
        fields = [
            'id', 'brand', 'model_fa', 'model_en', 'trim_fa', 'trim_en', 
            'production_year', 'specifications_fa', 'specifications_en', 'price_logs'
        ]
        read_only_fields = fields


class VehicleWriteSerializer(serializers.ModelSerializer):
    """
    WRITE-ONLY serializer for the Vehicle model.
    Accepts a brand ID and all multilingual fields for creating/updating.
    """
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all())

    class Meta:
        model = Vehicle
        # Allow writing to all new fields
        fields = [
            'brand', 'model_fa', 'model_en', 'trim_fa', 'trim_en', 
            'production_year', 'specifications_fa', 'specifications_en'
        ]

