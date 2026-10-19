from django.db import models
from config.categories import CATEGORIES

class Service(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField()
    categorie = models.CharField(max_length=100, choices=CATEGORIES, blank=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    publie = models.BooleanField(default=True)
    ordre = models.IntegerField(default=0)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom