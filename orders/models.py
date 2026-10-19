import uuid
from django.db import models
from products.models import Product

class Order(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
        ('remboursee', 'Remboursée'),
    ]

    produit = models.ForeignKey(Product, on_delete=models.PROTECT)
    email = models.EmailField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    transaction_id = models.CharField(max_length=100, blank=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    telechargements = models.PositiveIntegerField(default=0)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande {self.id} - {self.produit.nom} - {self.statut}"