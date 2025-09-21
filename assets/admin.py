from django.contrib import admin
from .models import Asset, AssetPriceLog

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name_en', 'name_fa', 'category', 'is_monitored')
    list_filter = ('category', 'is_monitored')
    search_fields = ('symbol', 'name_en', 'name_fa')
    list_editable = ('is_monitored',)
    ordering = ('symbol',)

@admin.register(AssetPriceLog)
class AssetPriceLogAdmin(admin.ModelAdmin):
    list_display = ('asset', 'price', 'high', 'low', 'change_amount', 'change_percent', 'timestamp')
    list_filter = ('timestamp', 'asset__category')
    search_fields = ('asset__symbol', 'asset__name_en', 'asset__name_fa')
    ordering = ('-timestamp',)
    readonly_fields = ('price', 'high', 'low', 'change_amount', 'change_percent', 'timestamp')
