import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from shop.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        'email': 'test@example.com',
        'username': 'testuser',
        'first_name': 'Test',
        'password': 'TestPass123!',
        'role': 'user'
    }


@pytest.fixture
def admin_data():
    return {
        'email': 'admin@example.com',
        'username': 'adminuser',
        'first_name': 'Admin',
        'password': 'AdminPass123!',
        'role': 'admin'
    }


@pytest.mark.django_db
class TestUserRegistration:
    
    def test_register_user_success(self, api_client, user_data):
        """Test successful user registration"""
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert response.data['user']['email'] == user_data['email']
        assert response.data['user']['role'] == 'user'
        assert 'token' in response.data['user']
    
    def test_register_admin_success(self, api_client, admin_data):
        """Test successful admin registration"""
        url = reverse('register')
        response = api_client.post(url, admin_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user']['role'] == 'admin'
    
    def test_register_duplicate_email(self, api_client, user_data):
        """Test registration with duplicate email"""
        url = reverse('register')
        api_client.post(url, user_data, format='json')
        
        # Try to register again with same email
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_register_missing_fields(self, api_client):
        """Test registration with missing required fields"""
        url = reverse('register')
        incomplete_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        response = api_client.post(url, incomplete_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_weak_password(self, api_client):
        """Test registration with weak password"""
        url = reverse('register')
        weak_password_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'password': '123',
            'role': 'user'
        }
        response = api_client.post(url, weak_password_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    
    def test_login_success(self, api_client, user_data):
        """Test successful login"""
    # Register user first
        register_url = reverse('register')
        register_response = api_client.post(register_url, user_data, format='json')
    
    # Make sure registration was successful
        assert register_response.status_code == status.HTTP_201_CREATED
    
    # Login
        login_url = reverse('login')
        login_data = {
            'email': user_data['email'],
            'password': user_data['password']
        }
        response = api_client.post(login_url, login_data, format='json')
    
    # Check response
        if response.status_code != status.HTTP_200_OK:
            print(f"Login failed with: {response.data}")  # Debug info
    
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert 'token' in response.data['user']
    
    def test_login_invalid_credentials(self, api_client, user_data):
        """Test login with invalid credentials"""
        # Register user first
        register_url = reverse('register')
        api_client.post(register_url, user_data, format='json')
        
        # Try login with wrong password
        login_url = reverse('login')
        login_data = {
            'email': user_data['email'],
            'password': 'WrongPassword123!'
        }
        response = api_client.post(login_url, login_data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, api_client):
        """Test login with non-existent user"""
        login_url = reverse('login')
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123!'
        }
        response = api_client.post(login_url, login_data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED