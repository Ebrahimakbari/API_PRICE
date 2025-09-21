from django.urls import path
from .views import AssetListCreateAPIView, AssetDetailAPIView, MonitoredAssetListView

urlpatterns = [
    path('assets/', AssetListCreateAPIView.as_view(), name='asset-list-create'),
    # Use <str:pk> because the primary key is the symbol (a string)
    path('assets/monitored/', MonitoredAssetListView.as_view(), name='asset-monitored-list'),
    path('assets/<str:pk>/', AssetDetailAPIView.as_view(), name='asset-detail'),
]
