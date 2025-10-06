from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Brand, Category, Color, Warranty, Seller,
    MobileImage, Specification, Variant, Mobile
)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('title_fa', 'title_en', 'code', 'is_premium', 'visibility')
    list_filter = ('is_premium', 'visibility', 'created_at')
    search_fields = ('title_fa', 'title_en', 'code')
    readonly_fields = ('api_id', 'created_at', 'updated_at')
    ordering = ('title_fa',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title_fa', 'title_en', 'code')
    search_fields = ('title_fa', 'title_en', 'code')
    readonly_fields = ('api_id', 'created_at', 'updated_at')
    ordering = ('title_fa',)

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('title', 'title_fa', 'title_en', 'hex_code_display')
    search_fields = ('title', 'title_fa', 'title_en')
    readonly_fields = ('api_id', 'created_at')
    
    def hex_code_display(self, obj):
        if obj.hex_code:
            return format_html(
                '<span style="background-color: {}; padding: 5px;">{}</span>',
                obj.hex_code,
                obj.hex_code
            )
        return '-'
    hex_code_display.short_description = 'Color'

@admin.register(Warranty)
class WarrantyAdmin(admin.ModelAdmin):
    list_display = ('title_fa', 'title_en')
    search_fields = ('title_fa', 'title_en')
    readonly_fields = ('api_id', 'created_at')
    ordering = ('title_fa',)

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('title', 'title_fa', 'code')
    search_fields = ('title', 'title_fa', 'code')
    readonly_fields = ('api_id', 'created_at', 'updated_at')
    ordering = ('title',)

class MobileImageInline(admin.TabularInline):
    model = MobileImage
    extra = 1
    readonly_fields = ('id', 'created_at')
    fields = ('url', 'thumbnail_url', 'webp_url', 'is_main')

class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 1
    readonly_fields = ('created_at',)
    fields = ('title', 'title_fa', 'value', 'value_fa')

class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1
    readonly_fields = ('api_id', 'created_at', 'updated_at')
    fields = (
        'color', 'warranty', 'seller',
        'selling_price', 'rrp_price',
        'availability', 'is_incredible'
    )

@admin.register(Mobile)
class MobileAdmin(admin.ModelAdmin):
    list_display = (
        'title_fa', 'brand', 'category',
        'rating_rate', 'rating_count',
        'average_price', 'status'
    )
    list_filter = (
        'status', 'brand', 'category',
        'is_jet_eligible', 'created_at'
    )
    search_fields = (
        'title_fa', 'title_en',
        'brand__title_fa', 'category__title_fa'
    )
    readonly_fields = (
        'api_id', 'slug', 'created_at',
        'updated_at', 'api_fetched_at'
    )
    inlines = [
        MobileImageInline,
        SpecificationInline,
        VariantInline
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title_fa', 'title_en', 'slug',
                'url', 'status', 'product_type'
            )
        }),
        ('Relations', {
            'fields': ('brand', 'category')
        }),
        ('Description', {
            'fields': (
                'description', 'test_title_fa',
                'test_title_en', 'alternate_name'
            )
        }),
        ('Metrics', {
            'fields': (
                'metric6', 'dimension2', 'dimension6',
                'dimension7', 'dimension9', 'dimension11', 'dimension20'
            )
        }),
        ('Rating', {
            'fields': (
                'rating_rate', 'rating_count',
                'review_rating_value', 'review_author_name',
                'review_date_published', 'review_body'
            )
        }),
        ('Services', {
            'fields': (
                'digiplus_services', 'digiplus_service_list',
                'digiplus_services_summary', 'is_jet_eligible',
                'is_general_location_jet_eligible', 'fast_shipping_text'
            )
        }),
        ('Identifiers', {
            'fields': ('mpn', 'sku', 'price_currency')
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at', 'api_fetched_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def average_price(self, obj):
        price = obj.average_price
        if price:
            return f"{price:,} IRR"
        return '-'
    average_price.short_description = 'Lowest Price'

@admin.register(MobileImage)
class MobileImageAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'is_main', 'url_preview')
    list_filter = ('is_main', 'created_at')
    readonly_fields = ('id', 'created_at')
    
    def url_preview(self, obj):
        if obj.url:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px;" />',
                obj.url
            )
        return '-'
    url_preview.short_description = 'Preview'

@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'title', 'value')
    search_fields = ('title', 'value', 'mobile__title_fa')
    readonly_fields = ('created_at',)

@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = (
        'mobile', 'color', 'warranty',
        'seller', 'selling_price', 'availability'
    )
    list_filter = (
        'color', 'warranty', 'seller',
        'is_incredible', 'availability'
    )
    search_fields = (
        'mobile__title_fa', 'color__title',
        'seller__title'
    )
    readonly_fields = (
        'api_id', 'created_at', 'updated_at'
    )
    
    def selling_price_display(self, obj):
        return f"{obj.selling_price:,} IRR"
    selling_price_display.short_description = 'Price'
