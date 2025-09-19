from django.db import models
from django.utils import timezone






class MotorcycleBrand(models.Model):
    """Stores motorcycle brand names. e.g., Kavir Motor"""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Motorcycle Brand"
        verbose_name_plural = "Motorcycle Brands"

    def __str__(self):
        return self.name

class Motorcycle(models.Model):
    """Stores the unique, static specifications of a motorcycle variant."""
    brand = models.ForeignKey(MotorcycleBrand, on_delete=models.CASCADE, related_name="motorcycles")
    model = models.CharField(max_length=100) # e.g., AGV 150
    trim = models.CharField(max_length=100, null=True, blank=True)
    production_year = models.PositiveSmallIntegerField(null=True, blank=True)
    origin = models.CharField(max_length=50, blank=True) # e.g., Iranian, Foreign

    class Meta:
        verbose_name = "Motorcycle"
        verbose_name_plural = "Motorcycles"
        constraints = [
            models.UniqueConstraint(
                fields=['brand', 'model', 'trim', 'production_year'], 
                name='unique_motorcycle_variant'
            )
        ]

    def __str__(self):
        year_str = f"({self.production_year})" if self.production_year else ""
        return f"{self.brand.name} {self.model} {self.trim or ''} {year_str}".strip()

class MotorcyclePriceLog(models.Model):
    """Records the price of a specific motorcycle on a given date from a specific source."""
    motorcycle = models.ForeignKey(Motorcycle, on_delete=models.CASCADE, related_name="price_logs")
    price = models.PositiveBigIntegerField()
    log_date = models.DateField(default=timezone.now)
    source = models.CharField(max_length=100) 

    class Meta:
        verbose_name = "Motorcycle Price Log"
        verbose_name_plural = "Motorcycle Price Logs"
        ordering = ['-log_date']
        constraints = [
            models.UniqueConstraint(fields=['motorcycle', 'log_date', 'source'], name='price_log_per_day_per_source')
        ]
        
    def __str__(self):
        return f"{self.motorcycle} | Price: {self.price:,} on {self.log_date}"