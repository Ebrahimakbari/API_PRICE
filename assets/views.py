from django.http import Http404
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Asset
from .serializers import AssetSerializer, AssetWriteSerializer
from permissions import IsAdminOrReadOnly




class AssetListCreateAPIView(APIView):
    """
    List all assets or create a new one.
    - Search with `?search=<term>`
    - Filter by category with `?category=<CATEGORY_NAME>`
    """
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, format=None):
        assets = Asset.objects.prefetch_related('price_logs').all()

        # Filtering by Category
        category = request.query_params.get('category', None)
        if category:
            assets = assets.filter(category__iexact=category)

        # Searching
        search_term = request.query_params.get('search', None)
        if search_term:
            query = (
                Q(symbol__icontains=search_term) |
                Q(name_fa__icontains=search_term) |
                Q(name_en__icontains=search_term)
            )
            assets = assets.filter(query)

        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = AssetWriteSerializer(data=request.data)
        if serializer.is_valid():
            asset = serializer.save()
            # Return the full object using the read serializer
            read_serializer = AssetSerializer(asset)
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssetDetailAPIView(APIView):
    """Retrieve, update or delete an asset instance."""
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            # The primary key for Asset is the 'symbol' field
            return Asset.objects.prefetch_related('price_logs').get(pk=pk)
        except Asset.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        asset = self.get_object(pk)
        serializer = AssetSerializer(asset)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        asset = self.get_object(pk)
        serializer = AssetWriteSerializer(asset, data=request.data)
        if serializer.is_valid():
            updated_asset = serializer.save()
            read_serializer = AssetSerializer(updated_asset)
            return Response(read_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        asset = self.get_object(pk)
        asset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MonitoredAssetListView(APIView):
    """
    A read-only endpoint that returns a curated list of "exclusive" assets
    marked for monitoring.
    """
    serializer_class = AssetSerializer 
    permission_classes = [IsAdminOrReadOnly]


    def get(self, request, format=None):
        monitored_assets = Asset.objects.filter(is_monitored=True).prefetch_related('price_logs')
        
        serializer = self.serializer_class(monitored_assets, many=True)
        return Response(serializer.data)
