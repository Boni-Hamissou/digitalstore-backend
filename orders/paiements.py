from decimal import Decimal, InvalidOperation

import requests

from .kkiapay import verify_transaction
from .models import Order


def confirmer_paiement_commande(commande, id_transaction):
    """Vérifie un paiement auprès de Kkiapay et passe la commande en payée.
    Retourne (reussi, message)."""
    if commande.statut == 'payee':
        return True, 'Déjà payée.'

    # Une même transaction ne peut pas servir à payer deux commandes
    if Order.objects.filter(transaction_id=id_transaction).exclude(pk=commande.pk).exists():
        return False, 'Transaction déjà utilisée.'

    try:
        donnees = verify_transaction(id_transaction)
    except requests.RequestException:
        return False, 'Vérification impossible pour le moment.'

    try:
        montant_paye = Decimal(str(donnees.get('amount')))
    except (InvalidOperation, TypeError):
        montant_paye = None

    if (
        donnees.get('status') == 'SUCCESS'
        and montant_paye is not None
        and montant_paye >= commande.montant
    ):
        commande.statut = 'payee'
        commande.transaction_id = id_transaction
        commande.save()
        return True, 'Payée.'

    return False, 'Paiement non confirmé.'