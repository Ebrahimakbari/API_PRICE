from django.urls import path
from .views import AssetListCreateAPIView, AssetDetailAPIView

urlpatterns = [
    path('assets/', AssetListCreateAPIView.as_view(), name='asset-list-create'),
    # Use <str:pk> because the primary key is the symbol (a string)
    path('assets/<str:pk>/', AssetDetailAPIView.as_view(), name='asset-detail'),
]
