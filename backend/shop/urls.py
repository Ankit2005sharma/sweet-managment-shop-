from django.urls import path
from .views.auth_views import register_view, login_view
from .views.sweet_views import sweets_view, purchase_sweet


urlpatterns = [
    # AUTH
    path("auth/register/", register_view),
    path("auth/login/", login_view),

    # SWEETS
    path("sweets/", sweets_view),
    path("sweets/<int:pk>/purchase/", purchase_sweet),
]
