from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Prefetch
from .models import (
    Brand, Category, PriceHistory, Product, Variant, ProductImage,
    ReviewAttribute, SpecGroup, SpecAttribute, ProductSpecification
)


class PriceHistoryInline(admin.TabularInline):
    model = PriceHistory
    extra = 0
    readonly_fields = ('timestamp',)
    fields = ('selling_price', 'rrp_price', 'timestamp')
    ordering = ('-timestamp',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'title_fa', 'code', 'created_at', 'image_preview')
    search_fields = ('title_en', 'title_fa', 'code')
    list_filter = ('created_at',)
    ordering = ('title_en',)
    readonly_fields = ('api_id', 'created_at', 'updated_at', 'image_preview')
    
    def image_preview(self, obj):
        if obj.logo_url:
            return format_html(
                '<img src="{}" style="width: 45px; height: 45px; object-fit: cover;" />',
                obj.logo_url
            )
        return "No Image"
    image_preview.short_description = 'Image'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title_fa', 'title_en', 'code', 'created_at')
    search_fields = ('title_fa', 'title_en', 'code')
    list_filter = ('created_at',)
    ordering = ('title_fa',)
    readonly_fields = ('api_id', 'created_at', 'updated_at')

class ReviewAttributeInline(admin.TabularInline):
    model = ReviewAttribute
    extra = 1
    fields = ('title', 'value')

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1
    fields = ('attribute', 'value')
    raw_id_fields = ('attribute',)

class VariantInline(admin.TabularInline):
    model = Variant
    extra = 0
    fields = ('api_id', 'seller_name', 'color_preview', 'color_name', 'color_hex',
              'warranty_name', 'selling_price', 'rrp_price')
    readonly_fields = ('api_id', 'color_preview')
    inlines = [PriceHistoryInline]

    
    def color_preview(self, obj):
        if obj.color_hex:
            return format_html(
                '<div style="width: 30px; height: 30px; background-color: {}; '
                'border: 1px solid #ccc; border-radius: 3px;"></div>',
                obj.color_hex
            )
        return "No Color"
    color_preview.short_description = 'Color'

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ('image_preview', 'is_main')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="width: 45px; height: 45px; object-fit: cover;" />',
                obj.image_url
            )
        return "No Image"
    image_preview.short_description = 'Image'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'title_fa', 'brand', 'category', 'status', 
                   'rating_rate', 'rating_count', 'main_image_preview', 
                   'current_price', 'price_history_preview', 'created_at')
    search_fields = ('title_en', 'title_fa', 'brand__title_en', 'brand__title_fa')
    list_filter = ('status', 'brand', 'category', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('api_id', 'slug', 'created_at', 'updated_at', 'price_history_preview')
    inlines = [VariantInline, ProductImageInline, ReviewAttributeInline, 
               ProductSpecificationInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('api_id', 'slug', 'title_fa', 'title_en', 'status', 'brand', 'category')
        }),
        ('Rating', {
            'fields': ('rating_rate', 'rating_count')
        }),
        ('Review', {
            'fields': ('review_description',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def main_image_preview(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image and main_image.image_url:
            return format_html(
                '<img src="{}" style="width: 45px; height: 45px; object-fit: cover;" />',
                main_image.image_url
            )
        return "No Main Image"
    main_image_preview.short_description = 'Main Image'

    def current_price(self, obj):
        latest_variant = obj.variants.first()
        if latest_variant:
            latest_price = latest_variant.price_history.first()
            if latest_price:
                return f"Current: {latest_price.selling_price} / RRP: {latest_price.rrp_price}"
        return "No Price"
    current_price.short_description = 'Current Price'

    def price_history_preview(self, obj):
        variants = obj.variants.all()
        if variants:
            history_html = []
            for variant in variants:
                prices = variant.price_history.all()[:3]  # Get last 3 price changes per variant
                if prices:
                    variant_history = [f"Variant {variant.api_id}:"]
                    for price in prices:
                        variant_history.append(
                            f"  {price.timestamp.strftime('%Y-%m-%d')}: {price.selling_price}"
                        )
                    history_html.append('<br>'.join(variant_history))
            if history_html:
                return format_html('<br><br>'.join(history_html))
        return "No Price History"
    price_history_preview.short_description = 'Recent Price Changes'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'brand', 'category'
        ).prefetch_related(
            Prefetch('variants', queryset=Variant.objects.all().order_by('-selling_price')),
            Prefetch(
                'variants__price_history',
                queryset=PriceHistory.objects.all().order_by('-timestamp'),
                to_attr='sorted_price_history'
            ),
            'images',
            'review_attributes',
            'specifications__attribute__group'
        )


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'seller_name', 'color_preview', 'color_name', 
                    'warranty_name', 'selling_price', 'rrp_price')
    search_fields = ('product__title_en', 'product__title_fa', 'seller_name', 'color_name')
    list_filter = ('warranty_name',)
    ordering = ('-selling_price',)
    readonly_fields = ('api_id',)
    inlines = [PriceHistoryInline]

    def color_preview(self, obj):
        if obj.color_hex:
            return format_html(
                '<div style="width: 30px; height: 30px; background-color: {}; '
                'border: 1px solid #ccc; border-radius: 3px;"></div>',
                obj.color_hex
            )
        return "No Color"
    color_preview.short_description = 'Color'

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview', 'is_main')
    search_fields = ('product__title_en', 'product__title_fa')
    list_filter = ('is_main',)
    ordering = ('-is_main',)

    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="width: 45px; height: 45px; object-fit: cover;" />',
                obj.image_url
            )
        return "No Image"
    image_preview.short_description = 'Image Preview'

@admin.register(SpecGroup)
class SpecGroupAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    ordering = ('title',)

@admin.register(SpecAttribute)
class SpecAttributeAdmin(admin.ModelAdmin):
    list_display = ('group', 'title')
    search_fields = ('title', 'group__title')
    list_filter = ('group',)
    ordering = ('group', 'title')

@admin.register(ReviewAttribute)
class ReviewAttributeAdmin(admin.ModelAdmin):
    list_display = ('product', 'title', 'value')
    search_fields = ('product__title_en', 'product__title_fa', 'title')
    list_filter = ('title',)
    ordering = ('product', 'title')

@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ('product', 'attribute', 'value_preview')
    search_fields = ('product__title_en', 'product__title_fa', 'attribute__title')
    list_filter = ('attribute__group', 'attribute')
    ordering = ('product', 'attribute__group', 'attribute')
    raw_id_fields = ('attribute',)

    def value_preview(self, obj):
        return obj.value[:50] + '...' if len(obj.value) > 50 else obj.value
    value_preview.short_description = 'Value'


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('variant', 'selling_price', 'rrp_price', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('variant__api_id', 'variant__product__name')
    readonly_fields = ('timestamp',)
    
    # Order by most recent price first
    ordering = ('-timestamp',)
    
    # Group by variant for better organization
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('variant', 'variant__product')
    
    def variant_display(self, obj):
        return f"{obj.variant.api_id} - {obj.variant.product.name}"
    
    # Better column name in admin
    variant_display.short_description = 'Variant'

    # Add date hierarchy for easy navigation
    date_hierarchy = 'timestamp'
    
    # Add pagination
    list_per_page = 25