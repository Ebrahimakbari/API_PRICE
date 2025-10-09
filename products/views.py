from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import PriceHistory, Product, Brand, Category
from .serializers import (
    PriceHistorySerializer, ProductSerializer, ProductListSerializer, BrandSerializer, CategorySerializer
)


class ProductListView(APIView):
    """
    Retrieve a list of Product phones with optional filtering and sorting.
    
    Query Parameters:
    - brand: Filter by brand ID
    - category: Filter by category ID
    - status: Filter by status
    - min_rating: Filter by minimum rating (inclusive)
    - search: Search in title_en and title_fa fields (case-insensitive)
    
    Returns:
    - List of Product phones sorted by rating (descending) and creation date (descending)
    """
    def get(self, request):
        queryset = Product.objects.all()
        brand_id = request.query_params.get('brand')
        category_id = request.query_params.get('category')
        status_filter = request.query_params.get('status')
        min_rating = request.query_params.get('min_rating')
        search = request.query_params.get('search')

        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if min_rating:
            queryset = queryset.filter(rating_rate__gte=float(min_rating))
        if search:
            queryset = queryset.filter(
                Q(title_en__icontains=search) | Q(title_fa__icontains=search)
            )

        queryset = queryset.order_by('-rating_rate', '-created_at')
        serializer = ProductListSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    """
    API endpoint to retrieve a specific Product by ID or slug.
    Supports PUT for updating and DELETE for removing the Product.
    """
    def get(self, request, lookup):
        try:
            pk = int(lookup)
            product = get_object_or_404(Product, pk=pk)
        except ValueError:
            product = get_object_or_404(Product, slug=lookup)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, lookup):
        try:
            pk = int(lookup)
            product = get_object_or_404(Product, pk=pk)
        except ValueError:
            product = get_object_or_404(Product, slug=lookup)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, lookup):
        try:
            pk = int(lookup)
            product = get_object_or_404(Product, pk=pk)
        except ValueError:
            product = get_object_or_404(Product, slug=lookup)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BrandListView(APIView):
    """
    API endpoint to list all brands, with optional search.
    Supports POST for creating new brands.
    """
    def get(self, request):
        queryset = Brand.objects.all()
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title_en__icontains=search) | Q(title_fa__icontains=search)
            )
        queryset = queryset.order_by('title_en')
        serializer = BrandSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BrandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BrandDetailView(APIView):
    """
    API endpoint to retrieve a specific brand by ID.
    Supports PUT for updating and DELETE for removing the brand.
    """
    def get(self, request, pk):
        brand = get_object_or_404(Brand, pk=pk)
        serializer = BrandSerializer(brand)
        return Response(serializer.data)

    def put(self, request, pk):
        brand = get_object_or_404(Brand, pk=pk)
        serializer = BrandSerializer(brand, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        brand = get_object_or_404(Brand, pk=pk)
        brand.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryListView(APIView):
    """
    API endpoint to list all categories, with optional search.
    Supports POST for creating new categories.
    """
    def get(self, request):
        queryset = Category.objects.all()
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title_en__icontains=search) | Q(title_fa__icontains=search)
            )
        queryset = queryset.order_by('title_fa')
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    """
    API endpoint to retrieve a specific category by ID.
    Supports PUT for updating and DELETE for removing the category.
    """
    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductSearchView(APIView):
    """
    API endpoint for advanced search of Products by title, brand, api_id or category.
    """
    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Query parameter "q" is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = Product.objects.filter(
            Q(title_en__icontains=query) |
            Q(title_fa__icontains=query) |
            Q(brand__title_en__icontains=query) |
            Q(brand__title_fa__icontains=query) |
            Q(api_id__iexact=query) |
            Q(category__title_fa__icontains=query)
        ).order_by('-rating_rate')
        
        serializer = ProductListSerializer(queryset, many=True)
        return Response(serializer.data)


class ProductPriceHistoryView(APIView):
    """
    Provides the price history for all variants of a specific product.
    """
    def get(self, request, lookup, format=None):
        """
        Handles the GET request to retrieve price history.
        """
        product_filter = Q(api_id=lookup)
        product = get_object_or_404(Product, product_filter)
        queryset = PriceHistory.objects.filter(
            variant__product=product
        ).select_related('variant').order_by('variant__api_id', '-timestamp')
        
        serializer = PriceHistorySerializer(queryset, many=True)
        return Response(serializer.data)
