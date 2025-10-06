from django.db import models

class Brand(models.Model):
    """Stores mobile phone brand information."""
    api_id = models.IntegerField(unique=True)
    title_fa = models.CharField(max_length=100)
    title_en = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=50, unique=True)
    logo_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title_en or self.title_fa

class Category(models.Model):
    """Stores product category information."""
    api_id = models.IntegerField(unique=True)
    title_fa = models.CharField(max_length=100)
    title_en = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title_fa

class Color(models.Model):
    """Stores color information for product variants."""
    api_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7)

    def __str__(self):
        return self.title

class Warranty(models.Model):
    """Stores warranty information for product variants."""
    api_id = models.IntegerField(unique=True)
    title_fa = models.CharField(max_length=255)

    def __str__(self):
        return self.title_fa

class Seller(models.Model):
    """Stores seller information."""
    api_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    url = models.URLField(max_length=500)

    def __str__(self):
        return self.title

class Mobile(models.Model):
    """Main model for a mobile phone product."""
    api_id = models.PositiveIntegerField(unique=True, help_text="The unique product ID from the API")
    title_fa = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name="mobiles")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="mobiles")
    
    # From the detail response's "review" section
    description = models.TextField(blank=True, null=True)
    
    # Store rating info
    rating_rate = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title_en

class MobileImage(models.Model):
    """Stores image URLs for a mobile phone."""
    mobile = models.ForeignKey(Mobile, on_delete=models.CASCADE, related_name="images")
    image_url = models.URLField(max_length=500, unique=True)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.mobile.title_en}"

class Specification(models.Model):
    """Stores key-value specifications for a mobile."""
    mobile = models.ForeignKey(Mobile, on_delete=models.CASCADE, related_name="specifications")
    title = models.CharField(max_length=100)
    value = models.CharField(max_length=255)

    class Meta:
        unique_together = ('mobile', 'title')

    def __str__(self):
        return f"{self.title}: {self.value}"

class Variant(models.Model):
    """Represents a specific variant of a mobile phone (e.g., color, seller)."""
    api_id = models.PositiveIntegerField(unique=True)
    mobile = models.ForeignKey(Mobile, on_delete=models.CASCADE, related_name="variants")
    
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    warranty = models.ForeignKey(Warranty, on_delete=models.SET_NULL, null=True)
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True)
    
    selling_price = models.PositiveIntegerField()
    rrp_price = models.PositiveIntegerField()
    order_limit = models.PositiveIntegerField()
    is_incredible = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.mobile.title_en} - {self.color.title} ({self.seller.title})"