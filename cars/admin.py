from django.contrib import admin

from cars.models import Brand, PriceLog, Vehicle

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name', 'trim', 'production_year', 'specifications')
    list_filter = ('brand', 'production_year')
    search_fields = ('name', 'trim', 'specifications')
    

@admin.register(PriceLog)
class PriceLogAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'price', 'log_date')
    list_filter = ('vehicle', 'log_date')
    search_fields = ('vehicle__name', 'vehicle__trim')
    ordering = ('-log_date',)

