from rest_framework import serializers
from .models import (
    Brand, Category, PriceHistory, Product, ReviewAttribute, SpecGroup, SpecAttribute,
    ProductSpecification, Variant, ProductImage
)


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'api_id', 'code', 'title_fa', 'title_en', 'logo_url', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'api_id', 'code', 'title_fa', 'title_en', 'created_at', 'updated_at']


class ReviewAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewAttribute
        fields = ['id', 'title', 'value']


class SpecGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecGroup
        fields = ['id', 'title']


class SpecAttributeSerializer(serializers.ModelSerializer):
    group = SpecGroupSerializer(read_only=True)

    class Meta:
        model = SpecAttribute
        fields = ['id', 'group', 'title']


class ProductSpecificationSerializer(serializers.ModelSerializer):
    attribute = SpecAttributeSerializer(read_only=True)

    class Meta:
        model = ProductSpecification
        fields = ['id', 'attribute', 'value']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'is_main']


class PriceHistorySerializer(serializers.ModelSerializer):
    """ Serializes a single price history entry. """
    class Meta:
        model = PriceHistory
        fields = ['selling_price', 'rrp_price', 'timestamp']


class VariantSerializer(serializers.ModelSerializer):
    price_history = PriceHistorySerializer(many=True, read_only=True)
    class Meta:
        model = Variant
        fields = ['id', 'api_id', 'seller_name', 'color_name', 'color_hex', 'warranty_name', 'selling_price', 'rrp_price', 'price_history']


class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    review_attributes = ReviewAttributeSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = VariantSerializer(many=True, read_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(), source='brand', write_only=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'api_id', 'slug', 'title_fa', 'title_en', 'status', 'brand', 'category',
            'rating_rate', 'rating_count', 'review_description', 'review_attributes',
            'specifications', 'images', 'variants', 'created_at', 'updated_at',
            'brand_id', 'category_id'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    variants = VariantSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    review_attributes = ReviewAttributeSerializer(many=True, read_only=True)
    cheapest_variant = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'api_id', 'slug', 'title_fa', 'title_en', 'status', 'brand', 'category','review_description',
            'rating_rate', 'rating_count', 'created_at', 'updated_at', 'variants', 'specifications', 'images',
            'review_attributes','cheapest_variant'
        ]
        
    def get_cheapest_variant(self, obj):
        # Provides a quick look at the current lowest price
        cheapest = obj.variants.order_by('selling_price').first()
        if cheapest:
            return {
                'selling_price': cheapest.selling_price,
                'rrp_price': cheapest.rrp_price
            }
        return None