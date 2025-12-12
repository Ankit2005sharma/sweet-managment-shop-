from django.urls import path
from shop.views.auth_views import register_view, login_view
from shop.views.sweet_views import sweets_view, purchase_sweet
from shop.views.order_views import orders_view

urlpatterns = [
    path("auth/register/", register_view),
    path("auth/login/", login_view),
    path("sweets/", sweets_view),
    path("sweets/<int:pk>/purchase/", purchase_sweet),
    path("orders/", orders_view),
]
