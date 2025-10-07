from django.db import models
from django.db.models import JSONField
import re

def simple_slugify(text):
    if not text:
        return ''
    text = re.sub(r'[^\w\s-]', '', str(text)).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    return text[:80] # Increased slug length slightly

class Brand(models.Model):
    api_id = models.IntegerField(unique=True)
    code = models.CharField(max_length=100, unique=True, db_index=True)
    title_fa = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True)
    logo_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title_en or self.title_fa

class Category(models.Model):
    api_id = models.IntegerField(unique=True)
    code = models.CharField(max_length=100, unique=True, db_index=True)
    title_fa = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title_fa

class Mobile(models.Model):
    api_id = models.PositiveIntegerField(unique=True, help_text="The unique product ID from the API")
    slug = models.SlugField(max_length=100, unique=True, blank=True, help_text="Auto-generated slug for clean URLs")
    title_fa = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='marketable', db_index=True)

    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="mobiles")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="mobiles")

    # Core product info
    rating_rate = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    
    # Store rich, nested JSON data directly
    review = JSONField(default=dict, blank=True, help_text="Stores the 'review' object from the API")
    specifications = JSONField(default=dict, blank=True, help_text="Stores the 'specifications' list from the API")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['brand', 'rating_rate']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.title_en or self.title_fa

    def save(self, *args, **kwargs):
        if not self.slug:
            slug_text = f"{self.api_id}-{self.title_en or self.title_fa}"
            self.slug = simple_slugify(slug_text)
        super().save(*args, **kwargs)

class Variant(models.Model):
    # Unique identifier from the API
    api_id = models.PositiveIntegerField(unique=True)
    mobile = models.ForeignKey(Mobile, on_delete=models.CASCADE, related_name="variants")
    seller_name = models.CharField(max_length=255, blank=True)
    color_name = models.CharField(max_length=100, blank=True)
    color_hex = models.CharField(max_length=7, blank=True)
    warranty_name = models.CharField(max_length=255, blank=True)
    
    selling_price = models.PositiveIntegerField(default=0)
    rrp_price = models.PositiveIntegerField(default=0)
    order_limit = models.PositiveIntegerField(default=1)
    is_incredible = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('mobile', 'api_id')

class MobileImage(models.Model):
    mobile = models.ForeignKey(Mobile, on_delete=models.CASCADE, related_name="images")
    image_url = models.URLField(max_length=500)
    is_main = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('mobile', 'image_url')