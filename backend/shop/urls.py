from django.urls import path
from . import views

urlpatterns = [
    # Auth endpoints
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    
    # Sweet endpoints
    path('sweets/', views.SweetListCreateView.as_view(), name='sweet-list-create'),
    path('sweets/<int:pk>/', views.SweetDetailView.as_view(), name='sweet-detail'),
    path('sweets/search/', views.search_sweets, name='sweet-search'),
    
    # Inventory endpoints
    path('sweets/<int:pk>/purchase/', views.purchase_sweet, name='purchase-sweet'),
    path('sweets/<int:pk>/restock/', views.restock_sweet, name='restock-sweet'),
    
    # Orders
    path('orders/my/', views.my_orders, name='my-orders'),
]