from django.contrib import admin
from motorcycles.models import Motorcycle, MotorcycleBrand, MotorcyclePriceLog





@admin.register(MotorcycleBrand)
class MotorcycleBrandAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Motorcycle)
class MotorcycleAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'trim', 'production_year', 'origin')
    list_filter = ('brand', 'production_year', 'origin')
    search_fields = ('brand__name', 'model', 'trim')


@admin.register(MotorcyclePriceLog)
class MotorcyclePriceLogAdmin(admin.ModelAdmin):
    list_display = ('motorcycle', 'price', 'log_date', 'source')
    list_filter = ('motorcycle', 'log_date', 'source')
    search_fields = ('motorcycle__brand__name', 'motorcycle__model', 'motorcycle__trim', 'source')
