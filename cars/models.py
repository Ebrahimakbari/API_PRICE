from django.db import models
from django.utils import timezone





class Brand(models.Model):
    """
    Stores brand names to avoid redundancy.
    e.g., Peugeot, Saipa, Iran Khodro
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Brand Name")

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    """
    Stores the unique and static specifications of a vehicle variant.
    The combination of all fields here defines one specific type of car.
    """
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="vehicles", verbose_name="Brand")
    name = models.CharField(max_length=100, verbose_name="Vehicle Name")  # e.g., Pars, 207
    trim = models.CharField(max_length=100, verbose_name="Trim")  # e.g., LX-Tu5, Custom ELX
    production_year = models.PositiveSmallIntegerField(verbose_name="Production Year") # e.g., 2023
    specifications = models.CharField(max_length=255, verbose_name="Specifications", blank=True, help_text="e.g., Base, Full Option")

    class Meta:
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"
        # This constraint ensures you never save a duplicate vehicle variant.
        constraints = [
            models.UniqueConstraint(
                fields=['brand', 'name', 'trim', 'production_year', 'specifications'], 
                name='unique_vehicle_variant'
            )
        ]

    def __str__(self):
        return f"{self.brand.name} {self.name} - {self.trim} ({self.production_year})"


class PriceLog(models.Model):
    """
    Records the price of a specific vehicle on a given date.
    This is the core of your price history system.
    """
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="price_logs", verbose_name="Vehicle")
    price = models.PositiveBigIntegerField(verbose_name="Price")
    log_date = models.DateField(default=timezone.now, verbose_name="Log Date")

    class Meta:
        verbose_name = "Price Log"
        verbose_name_plural = "Price Logs"
        ordering = ['-log_date']
        constraints = [
            models.UniqueConstraint(fields=['vehicle', 'log_date'], name='price_log_per_day')
        ]
        
    def __str__(self):
        return f"{self.vehicle} | Price: {self.price:,} on {self.log_date}"