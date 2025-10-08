from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Prefetch
from .models import (
    Brand, Category, Mobile, Variant, MobileImage,
    ReviewAttribute, SpecGroup, SpecAttribute, MobileSpecification
)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'title_fa', 'code', 'created_at')
    search_fields = ('title_en', 'title_fa', 'code')
    list_filter = ('created_at',)
    ordering = ('title_en',)
    readonly_fields = ('api_id', 'created_at', 'updated_at')

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

class MobileSpecificationInline(admin.TabularInline):
    model = MobileSpecification
    extra = 1
    fields = ('attribute', 'value')
    raw_id_fields = ('attribute',)

class VariantInline(admin.TabularInline):
    model = Variant
    extra = 0
    fields = ('api_id', 'seller_name', 'color_preview', 'color_name', 'color_hex',
              'warranty_name', 'selling_price', 'rrp_price')
    readonly_fields = ('api_id', 'color_preview')
    
    def color_preview(self, obj):
        if obj.color_hex:
            return format_html(
                '<div style="width: 30px; height: 30px; background-color: {}; '
                'border: 1px solid #ccc; border-radius: 3px;"></div>',
                obj.color_hex
            )
        return "No Color"
    color_preview.short_description = 'Color'

class MobileImageInline(admin.TabularInline):
    model = MobileImage
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

@admin.register(Mobile)
class MobileAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'title_fa', 'brand', 'category', 'status', 
                   'rating_rate', 'rating_count', 'main_image_preview', 'created_at')
    search_fields = ('title_en', 'title_fa', 'brand__title_en', 'brand__title_fa')
    list_filter = ('status', 'brand', 'category', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('api_id', 'slug', 'created_at', 'updated_at')
    inlines = [VariantInline, MobileImageInline, ReviewAttributeInline, MobileSpecificationInline]
    
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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'brand', 'category'
        ).prefetch_related(
            Prefetch('variants', queryset=Variant.objects.all().order_by('-selling_price')),
            'images',
            'review_attributes',
            'specifications__attribute__group'
        )

@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'seller_name', 'color_preview', 'color_name', 
                   'warranty_name', 'selling_price', 'rrp_price')
    search_fields = ('mobile__title_en', 'mobile__title_fa', 'seller_name', 'color_name')
    list_filter = ('warranty_name',)
    ordering = ('-selling_price',)
    readonly_fields = ('api_id',)

    def color_preview(self, obj):
        if obj.color_hex:
            return format_html(
                '<div style="width: 30px; height: 30px; background-color: {}; '
                'border: 1px solid #ccc; border-radius: 3px;"></div>',
                obj.color_hex
            )
        return "No Color"
    color_preview.short_description = 'Color'

@admin.register(MobileImage)
class MobileImageAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'image_preview', 'is_main')
    search_fields = ('mobile__title_en', 'mobile__title_fa')
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
    list_display = ('mobile', 'title', 'value')
    search_fields = ('mobile__title_en', 'mobile__title_fa', 'title')
    list_filter = ('title',)
    ordering = ('mobile', 'title')

@admin.register(MobileSpecification)
class MobileSpecificationAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'attribute', 'value_preview')
    search_fields = ('mobile__title_en', 'mobile__title_fa', 'attribute__title')
    list_filter = ('attribute__group', 'attribute')
    ordering = ('mobile', 'attribute__group', 'attribute')
    raw_id_fields = ('attribute',)

    def value_preview(self, obj):
        return obj.value[:50] + '...' if len(obj.value) > 50 else obj.value
    value_preview.short_description = 'Value'
