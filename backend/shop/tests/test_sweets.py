import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from shop.models import User, Sweet


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
def sweet_data():
    return {
        'name': 'Gulab Jamun',
        'description': 'Sweet fried dough balls soaked in syrup',
        'price': '120.00',
        'quantity': 10,
        'category': 'traditional',
        'image': '🍯'
    }


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
class TestSweetList:
    """Test cases for listing sweets"""
    
    def test_list_sweets_unauthenticated(self, api_client, create_sweet):
        """Test listing sweets without authentication"""
        create_sweet(name='Sweet 1')
        create_sweet(name='Sweet 2')
        
        url = reverse('sweet-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
    
    def test_list_empty_sweets(self, api_client):
        """Test listing when no sweets exist"""
        url = reverse('sweet-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0
    
    def test_list_sweets_authenticated_user(self, api_client, create_regular_user, create_sweet):
        """Test listing sweets as authenticated user"""
        user = create_regular_user
        api_client.force_authenticate(user=user)
        
        create_sweet(name='Sweet 1')
        create_sweet(name='Sweet 2')
        create_sweet(name='Sweet 3')
        
        url = reverse('sweet-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
    
    def test_list_sweets_contains_all_fields(self, api_client, create_sweet):
        """Test that listed sweets contain all required fields"""
        create_sweet(name='Test Sweet', price=100, quantity=5)
        
        url = reverse('sweet-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        sweet_data = response.data[0]
        
        assert 'id' in sweet_data
        assert 'name' in sweet_data
        assert 'price' in sweet_data
        assert 'quantity' in sweet_data
        assert 'category' in sweet_data
        assert 'created_at' in sweet_data


@pytest.mark.django_db
class TestSweetCreate:
    """Test cases for creating sweets"""
    
    def test_create_sweet_as_admin(self, api_client, create_admin, sweet_data):
        """Test creating sweet as admin"""
        api_client.force_authenticate(user=create_admin)
        
        url = reverse('sweet-list-create')
        response = api_client.post(url, sweet_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == sweet_data['name']
        assert response.data['price'] == sweet_data['price']
        assert Sweet.objects.count() == 1
    
    def test_create_sweet_as_user(self, api_client, create_regular_user, sweet_data):
        """Test creating sweet as regular user (should fail)"""
        api_client.force_authenticate(user=create_regular_user)
        
        url = reverse('sweet-list-create')
        response = api_client.post(url, sweet_data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Sweet.objects.count() == 0
    
    def test_create_sweet_unauthenticated(self, api_client, sweet_data):
        """Test creating sweet without authentication"""
        url = reverse('sweet-list-create')
        response = api_client.post(url, sweet_data, format='json')
    
        assert response.status_code == status.HTTP_401_UNAUTHORIZED  
    
    def test_create_sweet_negative_price(self, api_client, create_admin, sweet_data):
        """Test creating sweet with negative price"""
        api_client.force_authenticate(user=create_admin)
        sweet_data['price'] = '-10.00'
        
        url = reverse('sweet-list-create')
        response = api_client.post(url, sweet_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Sweet.objects.count() == 0
    
    def test_create_sweet_negative_quantity(self, api_client, create_admin, sweet_data):
        """Test creating sweet with negative quantity"""
        api_client.force_authenticate(user=create_admin)
        sweet_data['quantity'] = -5
        
        url = reverse('sweet-list-create')
        response = api_client.post(url, sweet_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Sweet.objects.count() == 0
    
    def test_create_sweet_missing_name(self, api_client, create_admin, sweet_data):
        """Test creating sweet without name"""
        api_client.force_authenticate(user=create_admin)
        del sweet_data['name']
        
        url = reverse('sweet-list-create')
        response = api_client.post(url, sweet_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Sweet.objects.count() == 0
    
    def test_create_sweet_missing_price(self, api_client, create_admin, sweet_data):
        """Test creating sweet without price"""
        api_client.force_authenticate(user=create_admin)
        del sweet_data['price']
        
        url = reverse('sweet-list-create')
        response = api_client.post(url, sweet_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Sweet.objects.count() == 0
    
    def test_create_multiple_sweets(self, api_client, create_admin, sweet_data):
        """Test creating multiple sweets"""
        api_client.force_authenticate(user=create_admin)
        
        url = reverse('sweet-list-create')
        
        # Create first sweet
        response1 = api_client.post(url, sweet_data, format='json')
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Create second sweet with different name
        sweet_data['name'] = 'Rasgulla'
        response2 = api_client.post(url, sweet_data, format='json')
        assert response2.status_code == status.HTTP_201_CREATED
        
        assert Sweet.objects.count() == 2


@pytest.mark.django_db
class TestSweetRetrieve:
    """Test cases for retrieving a single sweet"""
    
    def test_retrieve_sweet(self, api_client, create_sweet):
        """Test retrieving a single sweet"""
        sweet = create_sweet(name='Test Sweet', price=100)
        
        url = reverse('sweet-detail', kwargs={'pk': sweet.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Test Sweet'
        assert response.data['id'] == sweet.id
    
    def test_retrieve_nonexistent_sweet(self, api_client):
        """Test retrieving a sweet that doesn't exist"""
        url = reverse('sweet-detail', kwargs={'pk': 9999})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestSweetUpdate:
    """Test cases for updating sweets"""
    
    def test_update_sweet_as_admin(self, api_client, create_admin, create_sweet):
        """Test updating sweet as admin"""
        sweet = create_sweet(name='Old Name', price=100)
        api_client.force_authenticate(user=create_admin)
        
        url = reverse('sweet-detail', kwargs={'pk': sweet.pk})
        update_data = {
            'name': 'New Name',
            'price': '150.00',
            'quantity': 20,
            'category': 'modern',
            'image': '🍭'
        }
        response = api_client.put(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'New Name'
        assert response.data['price'] == '150.00'
        
        sweet.refresh_from_db()
        assert sweet.name == 'New Name'
        assert float(sweet.price) == 150.00
    
    def test_update_sweet_partial(self, api_client, create_admin, create_sweet):
        """Test partial update of sweet (PATCH)"""
        sweet = create_sweet(name='Old Name', price=100, quantity=10)
        api_client.force_authenticate(user=create_admin)
        
        url = reverse('sweet-detail', kwargs={'pk': sweet.pk})
        update_data = {'name': 'Updated Name'}
        response = api_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Name'
        
        sweet.refresh_from_db()
        assert sweet.name == 'Updated Name'
        assert float(sweet.price) == 100.00  # Price unchanged
    
    def test_update_sweet_as_user(self, api_client, create_regular_user, create_sweet):
        """Test updating sweet as regular user (should fail)"""
        sweet = create_sweet()
        api_client.force_authenticate(user=create_regular_user)
        
        url = reverse('sweet-detail', kwargs={'pk': sweet.pk})
        update_data = {
            'name': 'New Name',
            'price': '150.00',
            'quantity': 20,
            'category': 'modern'
        }
        response = api_client.put(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    
    def test_update_sweet_unauthenticated(self, api_client, create_sweet):
        """Test updating sweet without authentication"""
        sweet = create_sweet()
    
        url = reverse('sweet-detail', kwargs={'pk': sweet.pk})
        update_data = {
            'name': 'New Name',
            'price': '150.00',
            'quantity': 20,
            'category': 'modern'
        }
        response = api_client.put(url, update_data, format='json')
    
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_sweet_nonexistent(self, api_client, create_admin):
        """Test updating a sweet that doesn't exist"""
        api_client.force_authenticate(user=create_admin)
        
        url = reverse('sweet-detail', kwargs={'pk': 9999})
        update_data = {
            'name': 'New Name',
            'price': '150.00',
            'quantity': 20,
            'category': 'modern'
        }
        response = api_client.put(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestSweetDelete:
    """Test cases for deleting sweets"""
    
    def test_delete_sweet_as_admin(self, api_client, create_admin, create_sweet):
        """Test deleting sweet as admin"""
        sweet = create_sweet()
        api_client.force_authenticate(user=create_admin)
        
        url = reverse('sweet-detail', kwargs={'pk': sweet.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Sweet.objects.count() == 0
    
    def test_delete_sweet_as_user(self, api_client, create_regular_user, create_sweet):
        """Test deleting sweet as regular user (should fail)"""
        sweet = create_sweet()
        api_client.force_authenticate(user=create_regular_user)
        
        url = reverse('sweet-detail', kwargs={'pk': sweet.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Sweet.objects.count() == 1
    
    def test_delete_sweet_unauthenticated(self, api_client, create_sweet):
        """Test deleting sweet without authentication"""
        sweet = create_sweet()
    
        url = reverse('sweet-detail', kwargs={'pk': sweet.pk})
        response = api_client.delete(url)
    
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 
    
    def test_delete_sweet_nonexistent(self, api_client, create_admin):
        """Test deleting a sweet that doesn't exist"""
        api_client.force_authenticate(user=create_admin)
        
        url = reverse('sweet-detail', kwargs={'pk': 9999})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_multiple_sweets(self, api_client, create_admin, create_sweet):
        """Test deleting multiple sweets"""
        sweet1 = create_sweet(name='Sweet 1')
        sweet2 = create_sweet(name='Sweet 2')
        sweet3 = create_sweet(name='Sweet 3')
        
        api_client.force_authenticate(user=create_admin)
        
        assert Sweet.objects.count() == 3
        
        # Delete first sweet
        url1 = reverse('sweet-detail', kwargs={'pk': sweet1.pk})
        response1 = api_client.delete(url1)
        assert response1.status_code == status.HTTP_204_NO_CONTENT
        assert Sweet.objects.count() == 2
        
        # Delete second sweet
        url2 = reverse('sweet-detail', kwargs={'pk': sweet2.pk})
        response2 = api_client.delete(url2)
        assert response2.status_code == status.HTTP_204_NO_CONTENT
        assert Sweet.objects.count() == 1


@pytest.mark.django_db
class TestSweetSearch:
    """Test cases for searching sweets"""
    
    def test_search_by_name(self, api_client, create_sweet):
        """Test searching sweets by name"""
        create_sweet(name='Gulab Jamun')
        create_sweet(name='Rasgulla')
        create_sweet(name='Jalebi')
        
        url = reverse('sweet-search')
        response = api_client.get(url, {'name': 'gulab'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'Gulab Jamun'
    
    def test_search_by_name_case_insensitive(self, api_client, create_sweet):
        """Test case-insensitive name search"""
        create_sweet(name='Gulab Jamun')
        
        url = reverse('sweet-search')
        response = api_client.get(url, {'name': 'GULAB'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
    
    def test_search_by_category(self, api_client, create_sweet):
        """Test searching sweets by category"""
        create_sweet(name='Sweet 1', category='traditional')
        create_sweet(name='Sweet 2', category='modern')
        create_sweet(name='Sweet 3', category='traditional')
        
        url = reverse('sweet-search')
        response = api_client.get(url, {'category': 'traditional'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
    
    def test_search_by_min_price(self, api_client, create_sweet):
        """Test searching sweets by minimum price"""
        create_sweet(name='Cheap', price=50)
        create_sweet(name='Medium', price=100)
        create_sweet(name='Expensive', price=200)
        
        url = reverse('sweet-search')
        response = api_client.get(url, {'min_price': 100})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
    
    def test_search_by_max_price(self, api_client, create_sweet):
        """Test searching sweets by maximum price"""
        create_sweet(name='Cheap', price=50)
        create_sweet(name='Medium', price=100)
        create_sweet(name='Expensive', price=200)
        
        url = reverse('sweet-search')
        response = api_client.get(url, {'max_price': 100})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
    
    def test_search_by_price_range(self, api_client, create_sweet):
        """Test searching sweets by price range"""
        create_sweet(name='Cheap', price=50)
        create_sweet(name='Medium', price=100)
        create_sweet(name='Expensive', price=200)
        
        url = reverse('sweet-search')
        response = api_client.get(url, {'min_price': 75, 'max_price': 150})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'Medium'
    
    def test_search_combined_filters(self, api_client, create_sweet):
        """Test searching with multiple filters"""
        create_sweet(name='Traditional Sweet', category='traditional', price=100)
        create_sweet(name='Modern Sweet', category='modern', price=150)
        create_sweet(name='Traditional Expensive', category='traditional', price=300)
        
        url = reverse('sweet-search')
        response = api_client.get(url, {
            'category': 'traditional',
            'max_price': 200
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'Traditional Sweet'
    
    def test_search_no_results(self, api_client, create_sweet):
        """Test search with no matching results"""
        create_sweet(name='Gulab Jamun')
        create_sweet(name='Rasgulla')
        
        url = reverse('sweet-search')
        response = api_client.get(url, {'name': 'nonexistent'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0
    
    def test_search_without_filters(self, api_client, create_sweet):
        """Test search without any filters returns all sweets"""
        create_sweet(name='Sweet 1')
        create_sweet(name='Sweet 2')
        create_sweet(name='Sweet 3')
        
        url = reverse('sweet-search')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3


@pytest.mark.django_db
class TestSweetEdgeCases:
    """Test edge cases for sweet operations"""
    
    def test_create_sweet_with_zero_quantity(self, api_client, create_admin, sweet_data):
        """Test creating sweet with zero quantity"""
        api_client.force_authenticate(user=create_admin)
        sweet_data['quantity'] = 0
        
        url = reverse('sweet-list-create')
        response = api_client.post(url, sweet_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['quantity'] == 0
    
    def test_create_sweet_with_very_high_price(self, api_client, create_admin, sweet_data):
        """Test creating sweet with very high price"""
        api_client.force_authenticate(user=create_admin)
        sweet_data['price'] = '999999.99'
        
        url = reverse('sweet-list-create')
        response = api_client.post(url, sweet_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['price'] == '999999.99'
    
    def test_update_sweet_to_zero_quantity(self, api_client, create_admin, create_sweet):
        """Test updating sweet quantity to zero"""
        sweet = create_sweet(quantity=10)
        api_client.force_authenticate(user=create_admin)
        
        url = reverse('sweet-detail', kwargs={'pk': sweet.pk})
        update_data = {
            'name': sweet.name,
            'price': str(sweet.price),
            'quantity': 0,
            'category': sweet.category
        }
        response = api_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['quantity'] == 0