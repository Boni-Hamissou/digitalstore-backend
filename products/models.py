from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models import Max
from config.categories import CATEGORIES

def private_storage():
    return FileSystemStorage(location=settings.PRIVATE_ROOT)

from django.db import models

class Product(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField()
    description_detaillee = models.TextField(blank=True, help_text="Ce que contient le produit et les problèmes qu'il résout")
    video_url = models.URLField(blank=True, help_text="Lien YouTube de la démo (vidéo non répertoriée)")
    categorie = models.CharField(max_length=100, choices=CATEGORIES, blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    fichier = models.FileField(upload_to='products_files/', storage=private_storage, blank=True, null=True)
    problemes_resolus = models.TextField(blank=True, help_text="Un problème résolu par ligne")
    guide = models.FileField(upload_to='products_guides/', storage=private_storage, blank=True, null=True)
    publie = models.BooleanField(default=True)
    ordre = models.IntegerField(default=0)
    date_creation = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.pk and self.ordre == 0:
            dernier = Product.objects.aggregate(Max('ordre'))['ordre__max'] or 0
            self.ordre = dernier + 1
        super().save(*args, **kwargs)
    def __str__(self):
        return self.nom