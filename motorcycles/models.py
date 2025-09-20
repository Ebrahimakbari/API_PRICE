from django.db import models
from django.utils import timezone






class MotorcycleBrand(models.Model):
    """Stores motorcycle brand names (Persian display name and English slug)."""
    name_fa = models.CharField("Persian Name", max_length=100, unique=True)
    name_en_slug = models.CharField("English Slug", max_length=100, unique=True, null=True, blank=True)

    class Meta:
        verbose_name = "Motorcycle Brand"
        verbose_name_plural = "Motorcycle Brands"

    def __str__(self):
        return f"{self.name_fa} ({self.name_en_slug})" if self.name_en_slug else self.name_fa


class Motorcycle(models.Model):
    """Stores the unique specifications of a motorcycle variant."""
    brand = models.ForeignKey(MotorcycleBrand, on_delete=models.CASCADE, related_name="motorcycles")
    model_fa = models.CharField("Persian Model", max_length=100) # e.g., AGV 150
    model_en_slug = models.CharField("English Model Slug", max_length=100, null=True, blank=True) # e.g., agv150
    trim_fa = models.CharField("Persian Trim", max_length=100, null=True, blank=True) # The 'class' from the API
    production_year = models.PositiveSmallIntegerField("Production Year", null=True, blank=True)
    origin = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "Motorcycle"
        verbose_name_plural = "Motorcycles"
        constraints = [
            models.UniqueConstraint(
                fields=['brand', 'model_fa', 'trim_fa', 'production_year'], 
                name='unique_motorcycle_variant_fa'
            )
        ]

    def __str__(self):
        year_str = f"({self.production_year})" if self.production_year else ""
        return f"{self.brand.name_fa} {self.model_fa} {self.trim_fa or ''} {year_str}".strip()


class MotorcyclePriceLog(models.Model):
    """Records the price of a specific motorcycle. (No changes here)"""
    motorcycle = models.ForeignKey(Motorcycle, on_delete=models.CASCADE, related_name="price_logs")
    price = models.PositiveBigIntegerField("Price")
    log_date = models.DateField(default=timezone.now)
    source = models.CharField(max_length=100) 

    class Meta:
        verbose_name = "Motorcycle Price Log"
        verbose_name_plural = "Motorcycle Price Logs"
        ordering = ['-log_date']
        constraints = [
            models.UniqueConstraint(fields=['motorcycle', 'log_date', 'source'], name='motorcycle_price_log_per_day_per_source')
        ]
        
    def __str__(self):
        return f"{self.motorcycle} | Price: {self.price:,} on {self.log_date}"
