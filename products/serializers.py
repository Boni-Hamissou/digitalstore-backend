from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'nom', 'description', 'description_detaillee', 'video_url',
            'problemes_resolus', 'categorie', 'prix', 'image', 'publie',
            'ordre', 'date_creation',
        ]