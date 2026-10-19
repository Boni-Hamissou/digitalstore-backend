
import hmac

from django.conf import settings
from django.core.exceptions import ValidationError

from .paiements import confirmer_paiement_commande
import io
import os
import zipfile
from decimal import Decimal, InvalidOperation

import requests
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .kkiapay import verify_transaction
from .models import Order
from .serializers import OrderCreateSerializer, OrderStatusSerializer

MAX_TELECHARGEMENTS = 3
class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer


class OrderStatusView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusSerializer
    lookup_field = 'token'


@api_view(['POST'])
def confirm_payment(request, token):
    order = get_object_or_404(Order, token=token)

    if order.statut == 'payee':
        return Response({'statut': order.statut})

    transaction_id = str(request.data.get('transactionId', '')).strip()
    if not transaction_id:
        return Response(
            {'detail': 'transactionId manquant.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Une même transaction ne peut pas servir à payer deux commandes
    if Order.objects.filter(transaction_id=transaction_id).exclude(pk=order.pk).exists():
        return Response(
            {'detail': 'Transaction déjà utilisée.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        data = verify_transaction(transaction_id)
    except requests.RequestException:
        return Response(
            {'detail': 'Vérification impossible pour le moment.'},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    try:
        paid = Decimal(str(data.get('amount')))
    except (InvalidOperation, TypeError):
        paid = None

    if data.get('status') == 'SUCCESS' and paid is not None and paid >= order.montant:
        order.statut = 'payee'
        order.transaction_id = transaction_id
        order.save()
        return Response({'statut': order.statut})

    return Response(
        {'statut': order.statut, 'detail': 'Paiement non confirmé.'},
        status=status.HTTP_400_BAD_REQUEST,
    )


def download_order(request, token):
    order = get_object_or_404(Order, token=token)

    if order.statut != 'payee':
        raise Http404

    if order.telechargements >= MAX_TELECHARGEMENTS:
        return HttpResponse(
            "Limite de téléchargements atteinte. Contacte le support avec ton numéro de commande.",
            status=403,
        )

    produit = order.produit
    if not produit.fichier:
        raise Http404

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(produit.fichier.path, arcname=os.path.basename(produit.fichier.name))
        if produit.guide:
            zf.write(produit.guide.path, arcname='GUIDE_' + os.path.basename(produit.guide.name))
    buffer.seek(0)

    order.telechargements += 1
    order.save(update_fields=['telechargements'])

    return FileResponse(buffer, as_attachment=True, filename=f"{slugify(produit.nom)}.zip")

@api_view(['POST'])
def webhook_kkiapay(request):
    secret_recu = request.headers.get('x-kkiapay-secret', '')
    secret_attendu = settings.KKIAPAY_WEBHOOK_SECRET

    if not secret_attendu or not hmac.compare_digest(
        secret_recu.encode(), secret_attendu.encode()
    ):
        return Response({'detail': 'Non autorisé.'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.data.get('event') != 'transaction.success':
        return Response({'detail': 'Événement ignoré.'})

    id_transaction = str(request.data.get('transactionId', '')).strip()
    token = str(request.data.get('partnerId', '')).strip()
    if not id_transaction or not token:
        return Response({'detail': 'Données incomplètes.'})

    try:
        commande = Order.objects.get(token=token)
    except (Order.DoesNotExist, ValueError, ValidationError):
        return Response({'detail': 'Commande introuvable.'})

    reussi, message = confirmer_paiement_commande(commande, id_transaction)
    if not reussi and 'impossible' in message:
        # Erreur temporaire : Kkiapay réessaiera
        return Response({'detail': message}, status=status.HTTP_502_BAD_GATEWAY)

    return Response({'detail': message})