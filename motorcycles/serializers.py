from rest_framework import serializers
from .models import MotorcycleBrand, Motorcycle, MotorcyclePriceLog




class MotorcyclePriceLogSerializer(serializers.ModelSerializer):
    """Serializer for motorcycle price history."""
    class Meta:
        model = MotorcyclePriceLog
        fields = ['price', 'log_date', 'source']
        read_only_fields = fields


class MotorcycleBrandSerializer(serializers.ModelSerializer):
    """Serializer for the MotorcycleBrand model."""
    class Meta:
        model = MotorcycleBrand
        fields = ['id', 'name_fa', 'name_en_slug']


class MotorcycleSerializer(serializers.ModelSerializer):
    """
    READ-ONLY serializer for the Motorcycle model.
    Displays brand and price history as nested objects.
    """
    brand = MotorcycleBrandSerializer(read_only=True)
    price_logs = MotorcyclePriceLogSerializer(many=True, read_only=True)

    class Meta:
        model = Motorcycle
        fields = [
            'id', 'brand', 'model_fa', 'model_en_slug', 'trim_fa', 
            'production_year', 'origin', 'price_logs'
        ]
        read_only_fields = fields


class MotorcycleWriteSerializer(serializers.ModelSerializer):
    """
    WRITE-ONLY serializer for the Motorcycle model.
    Accepts a simple brand ID for creating/updating.
    """
    brand = serializers.PrimaryKeyRelatedField(queryset=MotorcycleBrand.objects.all())

    class Meta:
        model = Motorcycle
        # Allow writing to all new fields
        fields = ['brand', 'model_fa', 'model_en_slug', 'trim_fa', 'production_year', 'origin']