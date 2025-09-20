from django.urls import path
from . import views

urlpatterns = [
    # Brand URLs
    path('vehicles-brands/', views.BrandListCreateAPIView.as_view(), name='brand-list-create'),
    path('vehicles-brands/<int:pk>/', views.BrandDetailAPIView.as_view(), name='brand-detail'),

    # Vehicle URLs
    path('vehicles/', views.VehicleListCreateAPIView.as_view(), name='vehicle-list-create'),
    path('vehicles/<int:pk>/', views.VehicleDetailAPIView.as_view(), name='vehicle-detail'),
]
