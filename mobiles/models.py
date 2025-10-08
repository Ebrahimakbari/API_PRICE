from django.db import models
import re



def simple_slugify(text):
    """ Generate a simple slug from a string. """
    if not text:
        return ''
    text = re.sub(r'[^\w\s-]', '', str(text)).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    return text[:80]


class Brand(models.Model):
    """ Stores the brands from the API. """
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
    """ Stores the categories from the API. """
    api_id = models.IntegerField(unique=True)
    code = models.CharField(max_length=100, unique=True, db_index=True)
    title_fa = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title_fa
    
    
class Mobile(models.Model):
    """ Stores the mobiles from the API. """
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
    
    review_description = models.TextField(blank=True, null=True, help_text="Stores the 'description' from the review object")
    
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


class ReviewAttribute(models.Model):
    """ Stores the highlighted attributes from the 'review' section. """
    mobile = models.ForeignKey(Mobile, on_delete=models.CASCADE, related_name="review_attributes")
    title = models.CharField(max_length=255)
    value = models.CharField(max_length=500) 

    class Meta:
        unique_together = ('mobile', 'title') 

    def __str__(self):
        return f"{self.title}: {self.value}"


class SpecGroup(models.Model):
    """ A group for specifications, e.g., 'Display', 'Processor'. """
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title


class SpecAttribute(models.Model):
    """ A specific attribute within a group, e.g., 'Resolution', 'RAM'. """
    group = models.ForeignKey(SpecGroup, on_delete=models.CASCADE, related_name="attributes")
    title = models.CharField(max_length=100)

    class Meta:
        unique_together = ('group', 'title') 

    def __str__(self):
        return f"{self.group.title} - {self.title}"


class MobileSpecification(models.Model):
    """ Links a Mobile to a SpecAttribute and stores its specific value. """
    mobile = models.ForeignKey(Mobile, on_delete=models.CASCADE, related_name="specifications")
    attribute = models.ForeignKey(SpecAttribute, on_delete=models.PROTECT, related_name="mobile_values")
    value = models.TextField() # Use TextField to accommodate multiple or long values

    class Meta:
        unique_together = ('mobile', 'attribute')

    def __str__(self):
        return f"{self.mobile.title_en} - {self.attribute.title}: {self.value[:50]}"


class Variant(models.Model):
    """ Stores the variants of a mobile. """
    api_id = models.PositiveIntegerField(unique=True)
    mobile = models.ForeignKey(Mobile, on_delete=models.CASCADE, related_name="variants")
    seller_name = models.CharField(max_length=255, blank=True)
    color_name = models.CharField(max_length=100, blank=True)
    color_hex = models.CharField(max_length=7, blank=True)
    warranty_name = models.CharField(max_length=255, blank=True)
    selling_price = models.PositiveIntegerField(default=0)
    rrp_price = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('mobile', 'api_id')


class MobileImage(models.Model):
    """ Stores the images of a mobile. """
    mobile = models.ForeignKey(Mobile, on_delete=models.CASCADE, related_name="images")
    image_url = models.URLField(max_length=500)
    is_main = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('mobile', 'image_url')