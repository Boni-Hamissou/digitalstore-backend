from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'produit', 'email', 'montant', 'statut', 'telechargements', 'date_creation')
    list_filter = ('statut',)
    search_fields = ('email', 'transaction_id')
    readonly_fields = ('token',)