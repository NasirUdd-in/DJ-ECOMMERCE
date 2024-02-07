from django.urls import path
from .views import (
    Checkout,
    SaveOrder,
    Orders,
    seller_dashboard
 )
urlpatterns =[
    path('checkout/', Checkout.as_view(), name='checkout'),
    path('save-order/', SaveOrder.as_view(), name='save-order'),
    path('orders/', Orders.as_view(), name='orders'),
    path('seller_dashboard/', seller_dashboard, name='seller_dashboard'),
]