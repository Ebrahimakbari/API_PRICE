from django.urls import path
from . import views


urlpatterns = [
    # Brands
    path('products/brands/', views.BrandListView.as_view(), name='brand-list'),
    path('products/brands/<int:pk>/', views.BrandDetailView.as_view(), name='brand-detail'),

    # Categories
    path('products/categories/', views.CategoryListView.as_view(), name='category-list'),
    path('products/categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Products
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/search/', views.ProductSearchView.as_view(), name='product-search'),
    path('products/<str:lookup>/', views.ProductDetailView.as_view(), name='product-detail'),
    
    # e.g., /api/v1/products/iphone-14-pro/history/ or /api/v1/products/123/history/
    path('products/<str:lookup>/history/', views.ProductPriceHistoryView.as_view(), name='product-price-history'),
]
