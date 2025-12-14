import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from shop.models import User, Sweet, Order
from decimal import Decimal


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def make_user(email='user@example.com', role='user'):
        user = User.objects.create_user(
            username=email.split('@')[0],
            email=email,
            first_name='Test',
            password='TestPass123!',
            role=role
        )
        return user
    return make_user


@pytest.fixture
def create_admin(create_user):
    return create_user(email='admin@example.com', role='admin')


@pytest.fixture
def create_regular_user(create_user):
    return create_user(email='user@example.com', role='user')


@pytest.fixture
def create_sweet(create_admin):
    def make_sweet(**kwargs):
        default_data = {
            'name': 'Test Sweet',
            'price': 100,
            'quantity': 10,
            'category': 'traditional',
            'created_by': create_admin
        }
        default_data.update(kwargs)
        return Sweet.objects.create(**default_data)
    return make_sweet


@pytest.mark.django_db
class TestPurchase:
    
    def test_purchase_success(self, api_client, create_regular_user, create_sweet):
        """Test successful purchase"""
        user = create_regular_user
        sweet = create_sweet(quantity=10)
        api_client.force_authenticate(user=user)
        
        url = reverse('purchase-sweet', kwargs={'pk': sweet.pk})
        response = api_client.post(url, {'quantity': 1}, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['remaining_quantity'] == 9
        assert Order.objects.count() == 1
        
        sweet.refresh_from_db()
        assert sweet.quantity == 9
    
    def test_purchase_multiple_quantity(self, api_client, create_regular_user, create_sweet):
        """Test purchasing multiple quantities"""
        user = create_regular_user
        sweet = create_sweet(quantity=10, price=100)
        api_client.force_authenticate(user=user)
        
        url = reverse('purchase-sweet', kwargs={'pk': sweet.pk})
        response = api_client.post(url, {'quantity': 3}, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['remaining_quantity'] == 7
        
        order = Order.objects.first()
        assert order.quantity == 3
        assert order.total_price == Decimal('300.00')
    
    def test_purchase_insufficient_quantity(self, api_client, create_regular_user, create_sweet):
        """Test purchase with insufficient quantity"""
        user = create_regular_user
        sweet = create_sweet(quantity=2)
        api_client.force_authenticate(user=user)
        
        url = reverse('purchase-sweet', kwargs={'pk': sweet.pk})
        response = api_client.post(url, {'quantity': 5}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Insufficient quantity' in response.data['error']
    
    def test_purchase_out_of_stock(self, api_client, create_regular_user, create_sweet):
        """Test purchase when out of stock"""
        user = create_regular_user
        sweet = create_sweet(quantity=0)
        api_client.force_authenticate(user=user)
        
        url = reverse('purchase-sweet', kwargs={'pk': sweet.pk})
        response = api_client.post(url, {'quantity': 1}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_purchase_unauthenticated(self, api_client, create_sweet):
        """Test purchase without authentication"""
        sweet = create_sweet()
        
        url = reverse('purchase-sweet', kwargs={'pk': sweet.pk})
        response = api_client.post(url, {'quantity': 1}, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_purchase_nonexistent_sweet(self, api_client, create_regular_user):
        """Test purchase of non-existent sweet"""
        user = create_regular_user
        api_client.force_authenticate(user=user)
        
        url = reverse('purchase-sweet', kwargs={'pk': 9999})
        response = api_client.post(url, {'quantity': 1}, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_purchase_invalid_quantity(self, api_client, create_regular_user, create_sweet):
        """Test purchase with invalid quantity"""
        user = create_regular_user
        sweet = create_sweet()
        api_client.force_authenticate(user=user)
        
        url = reverse('purchase-sweet', kwargs={'pk': sweet.pk})
        response = api_client.post(url, {'quantity': -1}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRestock:
    
    def test_restock_success(self, api_client, create_admin, create_sweet):
        """Test successful restock"""
        admin = create_admin
        sweet = create_sweet(quantity=5)
        api_client.force_authenticate(user=admin)
        
        url = reverse('restock-sweet', kwargs={'pk': sweet.pk})
        response = api_client.post(url, {'quantity': 10}, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        sweet.refresh_from_db()
        assert sweet.quantity == 15
    
    def test_restock_as_user(self, api_client, create_regular_user, create_sweet):
        """Test restock as regular user (should fail)"""
        user = create_regular_user
        sweet = create_sweet()
        api_client.force_authenticate(user=user)
        
        url = reverse('restock-sweet', kwargs={'pk': sweet.pk})
        response = api_client.post(url, {'quantity': 10}, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_restock_unauthenticated(self, api_client, create_sweet):
        """Test restock without authentication"""
        sweet = create_sweet()
        
        url = reverse('restock-sweet', kwargs={'pk': sweet.pk})
        response = api_client.post(url, {'quantity': 10}, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_restock_invalid_quantity(self, api_client, create_admin, create_sweet):
        """Test restock with invalid quantity"""
        admin = create_admin
        sweet = create_sweet()
        api_client.force_authenticate(user=admin)
        
        url = reverse('restock-sweet', kwargs={'pk': sweet.pk})
        response = api_client.post(url, {'quantity': -5}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestOrders:
    
    def test_get_my_orders(self, api_client, create_regular_user, create_sweet):
        """Test getting user's orders"""
        user = create_regular_user
        sweet = create_sweet()
        api_client.force_authenticate(user=user)
        
        # Create some orders
        Order.objects.create(user=user, sweet=sweet, quantity=2, total_price=200)
        Order.objects.create(user=user, sweet=sweet, quantity=1, total_price=100)
        
        url = reverse('my-orders')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
    
    def test_get_orders_unauthenticated(self, api_client):
        """Test getting orders without authentication"""
        url = reverse('my-orders')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
