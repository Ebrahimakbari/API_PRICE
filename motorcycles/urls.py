from django.urls import path
from . import views

urlpatterns = [
    # MotorcycleBrand URLs
    path('motorcycle-brands/', views.MotorcycleBrandListCreateAPIView.as_view(), name='motorcycle-brand-list-create'),
    path('motorcycle-brands/<int:pk>/', views.MotorcycleBrandDetailAPIView.as_view(), name='motorcycle-brand-detail'),

    # Motorcycle URLs
    path('motorcycles/', views.MotorcycleListCreateAPIView.as_view(), name='motorcycle-list-create'),
    path('motorcycles/<int:pk>/', views.MotorcycleDetailAPIView.as_view(), name='motorcycle-detail'),
]
