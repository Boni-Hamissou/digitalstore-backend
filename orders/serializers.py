from rest_framework import serializers
from products.models import Product
from .models import Order

class OrderCreateSerializer(serializers.ModelSerializer):
    produit = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(publie=True)
    )

    class Meta:
        model = Order
        fields = ['id', 'produit', 'email', 'montant', 'statut', 'token']
        read_only_fields = ['id', 'montant', 'statut', 'token']

    def create(self, validated_data):
        produit = validated_data['produit']
        return Order.objects.create(
            produit=produit,
            email=validated_data['email'],
            montant=produit.prix,
        )

class OrderStatusSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)

    class Meta:
        model = Order
        fields = ['produit_nom', 'montant', 'statut', 'token']    