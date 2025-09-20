from django.http import Http404
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import MotorcycleBrand, Motorcycle
from .serializers import (
    MotorcycleBrandSerializer, 
    MotorcycleSerializer, 
    MotorcycleWriteSerializer
)
from permissions import IsAdminOrReadOnly



class MotorcycleBrandListCreateAPIView(APIView):
    """
    List all motorcycle brands or create a new one.
    - Search by `?search=<term>`
    """
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, format=None):
        brands = MotorcycleBrand.objects.all()
        
        search_term = request.query_params.get('search', None)
        if search_term:
            query = Q(name_fa__icontains=search_term) | Q(name_en_slug__icontains=search_term)
            brands = brands.filter(query)
            
        serializer = MotorcycleBrandSerializer(brands, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = MotorcycleBrandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MotorcycleBrandDetailAPIView(APIView):
    """Retrieve, update or delete a motorcycle brand instance."""
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return MotorcycleBrand.objects.get(pk=pk)
        except MotorcycleBrand.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        brand = self.get_object(pk)
        serializer = MotorcycleBrandSerializer(brand)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        brand = self.get_object(pk)
        serializer = MotorcycleBrandSerializer(brand, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        brand = self.get_object(pk)
        brand.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MotorcycleListCreateAPIView(APIView):
    """
    List all motorcycles or create a new one.
    - Search by `?search=<term>` across brand, model, and trim.
    """
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, format=None):
        motorcycles = Motorcycle.objects.select_related('brand').prefetch_related('price_logs').all()
        
        search_term = request.query_params.get('search', None)
        if search_term:
            query = (
                Q(model_fa__icontains=search_term) |
                Q(model_en_slug__icontains=search_term) |
                Q(trim_fa__icontains=search_term) |
                Q(brand__name_fa__icontains=search_term) |
                Q(brand__name_en_slug__icontains=search_term)
            )
            motorcycles = motorcycles.filter(query)

        serializer = MotorcycleSerializer(motorcycles, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = MotorcycleWriteSerializer(data=request.data)
        if serializer.is_valid():
            motorcycle = serializer.save()
            read_serializer = MotorcycleSerializer(motorcycle)
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MotorcycleDetailAPIView(APIView):
    """Retrieve, update or delete a motorcycle instance."""
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return Motorcycle.objects.select_related('brand').prefetch_related('price_logs').get(pk=pk)
        except Motorcycle.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        motorcycle = self.get_object(pk)
        serializer = MotorcycleSerializer(motorcycle)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        motorcycle = self.get_object(pk)
        serializer = MotorcycleWriteSerializer(motorcycle, data=request.data)
        if serializer.is_valid():
            updated_motorcycle = serializer.save()
            read_serializer = MotorcycleSerializer(updated_motorcycle)
            return Response(read_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        motorcycle = self.get_object(pk)
        motorcycle.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)