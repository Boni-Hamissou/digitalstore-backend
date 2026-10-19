from django.urls import path
from .views import OrderCreateView, OrderStatusView, confirm_payment, download_order, webhook_kkiapay

urlpatterns = [
    path('orders/', OrderCreateView.as_view(), name='order-create'),
    path('orders/<uuid:token>/', OrderStatusView.as_view(), name='order-status'),
    path('orders/<uuid:token>/confirm/', confirm_payment, name='order-confirm'),
    path('download/<uuid:token>/', download_order, name='order-download'),
    path('webhook/kkiapay/', webhook_kkiapay, name='webhook-kkiapay'),
]