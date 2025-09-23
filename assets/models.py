from django.db import models




class Asset(models.Model):
    """
    Represents a financial asset that can be tracked.
    Updated to store both Persian and English names.
    """
    CATEGORY_CHOICES = [
        ('COIN', 'Iranian Coins'),
        ('CURRENCY_IRR', 'Currency in IRR'),
        ('CURRENCY_FX', 'Forex Rates'),
        ('CRYPTO_IRR', 'Crypto in IRR'),
        ('CRYPTO_USD', 'Crypto in USD'),
        ('GOLD', 'Gold Variants'),
        ('METAL', 'Industrial & Precious Metals'),
        ('COMMODITY', 'Commodities'),
        ('INDEX', 'Stock Market Indices'),
        ('DERIVATIVES', 'Futures & Options'),
        ('OTHER', 'Other'),
    ]
    # The unique key from the API, e.g., "silver", "price_dollar_rl"
    symbol = models.CharField(max_length=100, unique=True, primary_key=True)
    name_fa = models.CharField(max_length=100, blank=True)
    name_en = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    is_monitored = models.BooleanField(default=False)

    def __str__(self):
        return self.name_fa or self.symbol


class AssetPriceLog(models.Model):
    """
    Stores a snapshot of an asset's price data at a specific point in time.
    (This model requires no changes)
    """
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="price_logs")
    price = models.DecimalField(max_digits=20, decimal_places=4)
    high = models.DecimalField(max_digits=20, decimal_places=4)
    low = models.DecimalField(max_digits=20, decimal_places=4)
    change_amount = models.DecimalField(max_digits=20, decimal_places=4)
    change_percent = models.FloatField()
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ['-timestamp']
        unique_together = ('asset', 'timestamp')

    def __str__(self):
        return f"{self.asset} - {self.price} @ {self.timestamp}"
