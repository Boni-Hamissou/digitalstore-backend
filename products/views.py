from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(publie=True).order_by('ordre')
    serializer_class = ProductSerializer

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(publie=True)
    serializer_class = ProductSerializer