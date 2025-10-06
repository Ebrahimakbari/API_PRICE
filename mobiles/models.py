from django.db import models
import uuid
from django.db.models import JSONField  # Use this for JSONField
import re

def simple_slugify(text):
    """
    Simple slugify function without external dependency.
    """
    if not text:
        return ''
    # Replace spaces and special chars with -
    text = re.sub(r'[^\w\s-]', '', str(text)).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    return text[:50]  # Limit length

class Brand(models.Model):
    """
    Model to store unique brands from the API.
    """
    api_id = models.IntegerField(unique=True, blank=True, null=True)  # API-provided ID, optional
    code = models.CharField(max_length=100, unique=True)  # e.g., "daria"
    title_fa = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    visibility = models.BooleanField(default=True)
    logo_url = models.URLField(blank=True, null=True)  # Main logo URL
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'brands'
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'

    def __str__(self):
        return self.title_fa or self.title_en


class Category(models.Model):
    """
    Model to store product category information.
    """
    api_id = models.IntegerField(unique=True, blank=True, null=True)  # Optional
    code = models.CharField(max_length=50, unique=True)
    title_fa = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title_fa


class Color(models.Model):
    """
    Model to store color information for product variants.
    """
    api_id = models.IntegerField(unique=True, blank=True, null=True)  # Optional
    title = models.CharField(max_length=100)
    title_fa = models.CharField(max_length=100, blank=True, null=True)
    title_en = models.CharField(max_length=100, blank=True, null=True)
    hex_code = models.CharField(max_length=7, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'colors'
        verbose_name = 'Color'
        verbose_name_plural = 'Colors'

    def __str__(self):
        return self.title


class Warranty(models.Model):
    """
    Model to store warranty information for product variants.
    """
    api_id = models.IntegerField(unique=True, blank=True, null=True)  # Optional
    title_fa = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'warranties'
        verbose_name = 'Warranty'
        verbose_name_plural = 'Warranties'

    def __str__(self):
        return self.title_fa


class Seller(models.Model):
    """
    Model to store seller information.
    """
    api_id = models.IntegerField(unique=True, blank=True, null=True)  # Optional
    title = models.CharField(max_length=255)
    title_fa = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=50, unique=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sellers'
        verbose_name = 'Seller'
        verbose_name_plural = 'Sellers'

    def __str__(self):
        return self.title


class MobileImage(models.Model):
    """
    Model to store multiple images for a mobile product.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mobile = models.ForeignKey('Mobile', on_delete=models.CASCADE, related_name='images')
    url = models.URLField(max_length=500)  # Full image URL
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    webp_url = models.URLField(max_length=500, blank=True, null=True)
    is_main = models.BooleanField(default=False)  # Flag for main image
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mobile_images'
        ordering = ['-is_main', 'id']
        verbose_name = 'Mobile Image'
        verbose_name_plural = 'Mobile Images'
        indexes = [models.Index(fields=['mobile', 'url'])]  # Partial unique for dedup

    def __str__(self):
        return f"Image for {self.mobile.title_fa[:50]}..."


class Specification(models.Model):
    """
    Model to store key-value specifications for a mobile.
    """
    mobile = models.ForeignKey('Mobile', on_delete=models.CASCADE, related_name="specifications")
    title = models.CharField(max_length=255)
    title_fa = models.CharField(max_length=255, blank=True, null=True)
    value = models.CharField(max_length=500)
    value_fa = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'specifications'
        unique_together = ('mobile', 'title')
        verbose_name = 'Specification'
        verbose_name_plural = 'Specifications'

    def __str__(self):
        return f"{self.title}: {self.value}"


class Variant(models.Model):
    """
    Model to represent a specific variant of a mobile phone (e.g., color, warranty, seller).
    """
    api_id = models.BigIntegerField(unique=True, blank=True, null=True)  # Optional for fallback variants, use BigInteger for large IDs
    mobile = models.ForeignKey('Mobile', on_delete=models.CASCADE, related_name="variants")
    
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, related_name="variants")
    warranty = models.ForeignKey(Warranty, on_delete=models.SET_NULL, null=True, related_name="variants")
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True, related_name="variants")
    
    # Pricing and availability
    selling_price = models.BigIntegerField()  # Current price, use BigInteger for large values
    rrp_price = models.BigIntegerField(blank=True, null=True)  # Recommended retail price, use BigInteger
    order_limit = models.PositiveIntegerField(default=1)
    is_incredible = models.BooleanField(default=False)  # e.g., special deal flag
    
    # Additional variant-specific fields
    availability = models.CharField(max_length=100, default='https://schema.org/InStock')
    is_jet_eligible = models.BooleanField(default=False)
    cash_back = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'variants'
        verbose_name = 'Variant'
        verbose_name_plural = 'Variants'
        indexes = [
            models.Index(fields=['mobile', 'selling_price']),
            models.Index(fields=['seller']),
        ]

    def __str__(self):
        return f"{self.mobile.title_fa[:50]} - {self.color.title if self.color else 'N/A'} ({self.seller.title if self.seller else 'N/A'})"


class Mobile(models.Model):
    """
    Core model to store mobile product details from the Digikala API.
    Uses the unique product ID as primary key.
    """
    api_id = models.PositiveIntegerField(primary_key=True)  # Unique product ID from API (e.g., 12017236)
    
    # Basic info
    title_fa = models.CharField(max_length=500)
    title_en = models.CharField(max_length=500, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)  # Derived from URL URI or title
    url = models.URLField(max_length=1000, blank=True, null=True)  # Full product URL, increased for long URIs
    status = models.CharField(max_length=50, default='marketable')  # e.g., 'marketable'
    product_type = models.CharField(max_length=50, default='product')
    
    # Brand and Category
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='mobiles')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='mobiles')
    
    # Description and content
    description = models.TextField(blank=True, null=True)  # Product description
    test_title_fa = models.CharField(max_length=500, blank=True, null=True)
    test_title_en = models.CharField(max_length=500, blank=True, null=True)
    alternate_name = models.CharField(max_length=500, blank=True, null=True)
    
    # Metrics and Dimensions (from data_layer)
    metric6 = models.IntegerField(blank=True, null=True)  # e.g., review count
    dimension2 = models.IntegerField(blank=True, null=True)  # e.g., 6
    dimension6 = models.IntegerField(blank=True, null=True)  # e.g., 0
    dimension7 = models.CharField(max_length=50, blank=True, null=True)  # e.g., "incredible"
    dimension9 = models.FloatField(blank=True, null=True)  # e.g., 4.5 (rating?)
    dimension11 = models.IntegerField(blank=True, null=True)  # e.g., 0
    dimension20 = models.CharField(max_length=50, blank=True, null=True)  # e.g., "marketable"
    
    # Rating and Reviews
    rating_rate = models.FloatField(default=0.0)  # Aggregate rating value
    rating_count = models.PositiveIntegerField(default=0)  # Review count
    
    # Sample Review (store one or latest)
    review_rating_value = models.IntegerField(blank=True, null=True)  # e.g., 5
    review_author_name = models.CharField(max_length=255, blank=True, null=True)
    review_date_published = models.DateField(blank=True, null=True)  # e.g., 2025-10-06
    review_body = models.TextField(blank=True, null=True)
    
    # Digiplus services (product-level)
    digiplus_services = JSONField(default=list)  # List of service strings, e.g., ["4 ارسال رایگان عادی"]
    digiplus_service_list = JSONField(default=list)  # Detailed list with titles
    digiplus_services_summary = JSONField(default=list)  # Summary list
    is_jet_eligible = models.BooleanField(default=False)
    is_general_location_jet_eligible = models.BooleanField(default=False)
    fast_shipping_text = models.TextField(blank=True, null=True)
    
    # Identifiers
    mpn = models.CharField(max_length=50, blank=True, null=True)  # Matches API ID
    sku = models.CharField(max_length=50, blank=True, null=True)
    price_currency = models.CharField(max_length=10, default='IRR')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    api_fetched_at = models.DateTimeField(auto_now_add=True)  # When last fetched from API

    class Meta:
        db_table = 'mobiles'
        verbose_name = 'Mobile'
        verbose_name_plural = 'Mobiles'
        indexes = [
            models.Index(fields=['brand', 'rating_rate']),
            models.Index(fields=['status']),
            models.Index(fields=['api_fetched_at']),
        ]

    def __str__(self):
        return self.title_fa[:100]

    def save(self, *args, **kwargs):
        # Auto-populate slug if not set (from title_fa or ID)
        if not self.slug:
            slug_text = f"{self.api_id}-{self.title_fa[:50]}"
            self.slug = simple_slugify(slug_text)
        super().save(*args, **kwargs)

    @property
    def average_price(self):
        """Get the lowest selling price from variants."""
        if self.variants.exists():
            return self.variants.aggregate(models.Min('selling_price'))['selling_price__min']
        return None