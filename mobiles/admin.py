from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Prefetch
import json
from .models import Brand, Category, Mobile, Variant, MobileImage

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

class VariantInline(admin.TabularInline):
    model = Variant
    extra = 0
    fields = ('api_id', 'seller_name', 'color_preview', 'color_name', 'color_hex',
              'warranty_name', 'selling_price', 'rrp_price', 'order_limit', 'is_incredible')
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
    readonly_fields = ('api_id', 'slug', 'created_at', 'updated_at', 
                      'formatted_review', 'formatted_specs')
    inlines = [VariantInline, MobileImageInline] 
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('api_id', 'slug', 'title_fa', 'title_en', 'status', 'brand', 'category')
        }),
        ('Rating', {
            'fields': ('rating_rate', 'rating_count')
        }),
        ('Review Data', {
            'fields': ('formatted_review',),
            'classes': ('collapse',)
        }),
        ('Specifications', {
            'fields': ('formatted_specs',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def formatted_review(self, obj):
        if obj.review:
            formatted_json = json.dumps(obj.review, indent=2, ensure_ascii=False)
            return format_html(
                '<pre style="white-space: pre-wrap; word-wrap: break-word;">{}</pre>',
                formatted_json
            )
        return "No Review Data"
    formatted_review.short_description = 'Review Details'

    def formatted_specs(self, obj):
        if obj.specifications:
            formatted_json = json.dumps(obj.specifications, indent=2, ensure_ascii=False)
            return format_html(
                '<pre style="white-space: pre-wrap; word-wrap: break-word;">{}</pre>',
                formatted_json
            )
        return "No Specification Data"
    formatted_specs.short_description = 'Specifications'

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
        return super().get_queryset(request).select_related('brand', 'category').prefetch_related(
            Prefetch('variants', queryset=Variant.objects.all().order_by('-selling_price')),
            'images'
        )

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        if obj:
            extra_context['variants_count'] = obj.variants.count()
            extra_context['images_count'] = obj.images.count()
        return super().change_view(request, object_id, form_url, extra_context)

@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'seller_name', 'color_preview', 'color_name', 
                   'warranty_name', 'selling_price', 'rrp_price', 'is_incredible')
    search_fields = ('mobile__title_en', 'mobile__title_fa', 'seller_name', 'color_name')
    list_filter = ('is_incredible', 'warranty_name')
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
