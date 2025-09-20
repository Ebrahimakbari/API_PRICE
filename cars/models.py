from django.db import models
from django.utils import timezone





class Brand(models.Model):
    """Stores car brand names in both Persian and English."""
    name_fa = models.CharField("Persian Name", max_length=100, unique=True)
    name_en = models.CharField("English Name", max_length=100, unique=True, null=True, blank=True)

    class Meta:
        verbose_name = "Car Brand"
        verbose_name_plural = "Car Brands"

    def __str__(self):
        return f"{self.name_fa} ({self.name_en})" if self.name_en else self.name_fa


class Vehicle(models.Model):
    """Stores the unique specifications of a car variant in both languages."""
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="vehicles", verbose_name="Brand")
    model_fa = models.CharField("Persian Model", max_length=100) # e.g., پارس
    model_en = models.CharField("English Model", max_length=100, null=True, blank=True) # e.g., Pars
    trim_fa = models.CharField("Persian Trim", max_length=100) # e.g., LX-Tu5
    trim_en = models.CharField("English Trim", max_length=100, null=True, blank=True) # e.g., LX-Tu5
    production_year = models.PositiveSmallIntegerField("Production Year")
    specifications_fa = models.CharField("Persian Specifications", max_length=255, blank=True) # e.g., بدون آپشن
    specifications_en = models.CharField("English Specifications", max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"
        constraints = [
            models.UniqueConstraint(
                fields=['brand', 'model_fa', 'trim_fa', 'production_year', 'specifications_fa'], 
                name='unique_car_variant_fa'
            )
        ]

    def __str__(self):
        return f"{self.brand.name_fa} {self.model_fa} - {self.trim_fa} ({self.production_year})"


class PriceLog(models.Model):
    """Records the price of a specific vehicle on a given date. (No changes here)"""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="price_logs", verbose_name="Vehicle")
    price = models.PositiveBigIntegerField("Price")
    log_date = models.DateField(default=timezone.now, verbose_name="Log Date")

    class Meta:
        verbose_name = "Car Price Log"
        verbose_name_plural = "Car Price Logs"
        ordering = ['-log_date']
        constraints = [
            models.UniqueConstraint(fields=['vehicle', 'log_date'], name='car_price_log_per_day')
        ]
        
    def __str__(self):
        return f"{self.vehicle} | Price: {self.price:,} on {self.log_date}"