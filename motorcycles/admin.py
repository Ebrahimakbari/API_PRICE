from django.contrib import admin
from .models import MotorcycleBrand, Motorcycle, MotorcyclePriceLog





@admin.register(MotorcycleBrand)
class MotorcycleBrandAdmin(admin.ModelAdmin):
    list_display = ('name_fa', 'name_en_slug')
    search_fields = ('name_fa', 'name_en_slug')
    list_per_page = 20

class MotorcyclePriceLogInline(admin.TabularInline):
    model = MotorcyclePriceLog
    extra = 0
    readonly_fields = ('price', 'log_date', 'source')
    can_delete = False
    max_num = 0


@admin.register(Motorcycle)
class MotorcycleAdmin(admin.ModelAdmin):
    list_display = ('model_fa', 'brand', 'production_year', 'origin', 'trim_fa')
    list_filter = ('brand', 'production_year', 'origin')
    search_fields = ('model_fa', 'model_en_slug', 'trim_fa')
    inlines = [MotorcyclePriceLogInline]
    ordering = ('brand', 'model_fa', 'production_year')
    list_per_page = 20


@admin.register(MotorcyclePriceLog)
class MotorcyclePriceLogAdmin(admin.ModelAdmin):
    list_display = ('motorcycle', 'price', 'log_date', 'source')
    list_filter = ('log_date', 'source')
    search_fields = ('motorcycle__model_fa', 'source')
    date_hierarchy = 'log_date'
    list_per_page = 20
    ordering = ('-log_date',)

    def has_add_permission(self, request):
        return False  # Don't allow manual addition of price logs

    def has_change_permission(self, request, obj=None):
        return False  # Don't allow modification of existing price logs