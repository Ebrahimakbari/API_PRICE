from django.http import Http404
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Brand, Vehicle
from .serializers import BrandSerializer, VehicleSerializer, VehicleWriteSerializer
from permissions import IsAdminOrReadOnly





class BrandListCreateAPIView(APIView):
    """
    List all brands or create a new brand.
    - Search by `?search=<term>` in both Persian and English names.
    """
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, format=None):
        brands = Brand.objects.all()
        
        search_term = request.query_params.get('search', None)
        if search_term:
            query = Q(name_fa__icontains=search_term) | Q(name_en__icontains=search_term)
            brands = brands.filter(query)
            
        serializer = BrandSerializer(brands, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = BrandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BrandDetailAPIView(APIView):
    """Retrieve, update or delete a brand instance."""
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return Brand.objects.get(pk=pk)
        except Brand.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        brand = self.get_object(pk)
        serializer = BrandSerializer(brand)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        brand = self.get_object(pk)
        serializer = BrandSerializer(brand, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        brand = self.get_object(pk)
        brand.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VehicleListCreateAPIView(APIView):
    """
    List all vehicles or create a new vehicle.
    - Search by `?search=<term>` across brand, model, and trim in both languages.
    """
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, format=None):
        vehicles = Vehicle.objects.select_related('brand').prefetch_related('price_logs').all()
        
        search_term = request.query_params.get('search', None)
        if search_term:
            query = (
                Q(model_fa__icontains=search_term) | Q(model_en__icontains=search_term) |
                Q(trim_fa__icontains=search_term) | Q(trim_en__icontains=search_term) |
                Q(brand__name_fa__icontains=search_term) | Q(brand__name_en__icontains=search_term)
            )
            vehicles = vehicles.filter(query)

        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = VehicleWriteSerializer(data=request.data)
        if serializer.is_valid():
            vehicle = serializer.save()
            read_serializer = VehicleSerializer(vehicle)
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VehicleDetailAPIView(APIView):
    """Retrieve, update or delete a vehicle instance."""
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return Vehicle.objects.select_related('brand').prefetch_related('price_logs').get(pk=pk)
        except Vehicle.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        vehicle = self.get_object(pk)
        serializer = VehicleSerializer(vehicle)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        vehicle = self.get_object(pk)
        serializer = VehicleWriteSerializer(vehicle, data=request.data)
        if serializer.is_valid():
            updated_vehicle = serializer.save()
            read_serializer = VehicleSerializer(updated_vehicle)
            return Response(read_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        vehicle = self.get_object(pk)
        vehicle.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)