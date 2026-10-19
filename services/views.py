from rest_framework import generics
from .models import Service
from .serializers import ServiceSerializer

class ServiceListView(generics.ListAPIView):
    queryset = Service.objects.filter(publie=True).order_by('ordre')
    serializer_class = ServiceSerializer