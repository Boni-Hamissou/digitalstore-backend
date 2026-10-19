import requests
from django.conf import settings


def verifier_transaction(id_transaction):
    url_base = (
        "https://api-sandbox.kkiapay.me"
        if settings.KKIAPAY_SANDBOX
        else "https://api.kkiapay.me"
    )
    reponse = requests.post(
        f"{url_base}/api/v1/transactions/status",
        json={"transactionId": id_transaction},
        headers={
            "Accept": "application/json",
            "X-API-KEY": settings.KKIAPAY_PUBLIC_KEY,
            "X-PRIVATE-KEY": settings.KKIAPAY_PRIVATE_KEY,
            "X-SECRET-KEY": settings.KKIAPAY_SECRET,
        },
        timeout=15,
    )
    reponse.raise_for_status()
    return reponse.json()


verify_transaction = verifier_transaction  # ancien nom, encore utilisé par views.py