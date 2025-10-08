from django.urls import path
from . import views


urlpatterns = [
    # Brands
    path('mobiles/brands/', views.BrandListView.as_view(), name='brand-list'),
    path('mobiles/brands/<int:pk>/', views.BrandDetailView.as_view(), name='brand-detail'),

    # Categories
    path('mobiles/categories/', views.CategoryListView.as_view(), name='category-list'),
    path('mobiles/categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Mobiles
    path('mobiles/', views.MobileListView.as_view(), name='mobile-list'),
    path('mobiles/<str:lookup>/', views.MobileDetailView.as_view(), name='mobile-detail'),
    path('mobiles/search/', views.MobileSearchView.as_view(), name='mobile-search'),
]
