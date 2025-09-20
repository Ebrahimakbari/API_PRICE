from django.contrib import admin
from .models import Brand, Vehicle, PriceLog




@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name_fa', 'name_en')
    search_fields = ('name_fa', 'name_en')
    list_per_page = 20
    ordering = ('name_fa',)

class PriceLogInline(admin.TabularInline):
    model = PriceLog
    extra = 0
    readonly_fields = ('price', 'log_date')
    can_delete = False
    max_num = 0
    fields = ('price', 'log_date')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('model_fa', 'brand', 'production_year', 'trim_fa', 'specifications_fa')
    list_filter = ('brand', 'production_year')
    search_fields = ('model_fa', 'model_en', 'trim_fa', 'trim_en')
    inlines = [PriceLogInline]
    ordering = ('brand', 'model_fa', 'production_year', 'trim_fa')
    list_per_page = 20
    fieldsets = (
        ('Basic Information', {
            'fields': ('brand', 'model_fa', 'model_en', 'production_year')
        }),
        ('Trim Details', {
            'fields': ('trim_fa', 'trim_en')
        }),
        ('Specifications', {
            'fields': ('specifications_fa', 'specifications_en')
        }),
    )

@admin.register(PriceLog)
class PriceLogAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'price', 'log_date')
    list_filter = ('log_date', 'vehicle__brand')
    search_fields = ('vehicle__model_fa', 'vehicle__trim_fa')
    date_hierarchy = 'log_date'
    list_per_page = 20
    ordering = ('-log_date',)

    def has_add_permission(self, request):
        return False  # Don't allow manual addition of price logs

    def has_change_permission(self, request, obj=None):
        return False  # Don't allow modification of existing price logs
