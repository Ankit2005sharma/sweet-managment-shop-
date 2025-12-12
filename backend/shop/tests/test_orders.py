import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from shop.models import Sweet


@pytest.mark.django_db
def test_create_order_success():
    """User should be able to create an order with valid quantities."""
    client = APIClient()

    # Create user
    user = User.objects.create_user(username="ankit", password="testpass")
    client.force_authenticate(user=user)

    # Create sweet
    sweet = Sweet.objects.create(name="Barfi", price=50, quantity=10)

    # Create order
    res = client.post("/api/orders/", {
        "items": [
            {"sweet": sweet.id, "quantity": 3}
        ]
    }, format="json")

    assert res.status_code == 201
    data = res.json()

    assert data["total_price"] == 150  # 50 * 3
    assert data["items"][0]["quantity"] == 3
    assert data["items"][0]["sweet"]["name"] == "Barfi"


@pytest.mark.django_db
def test_create_order_invalid_quantity():
    """Order should fail if requested quantity exceeds stock."""
    client = APIClient()
    
    user = User.objects.create_user(username="ankit", password="testpass")
    client.force_authenticate(user=user)

    sweet = Sweet.objects.create(name="Ladoo", price=10, quantity=2)

    res = client.post("/api/orders/", {
        "items": [
            {"sweet": sweet.id, "quantity": 5}
        ]
    }, format="json")

    assert res.status_code == 400
    assert "Not enough quantity" in res.json()["error"]


@pytest.mark.django_db
def test_user_can_view_only_their_orders():
    """User must only see their own orders."""
    client = APIClient()

    # Create users
    user1 = User.objects.create_user(username="ankit", password="pass1")
    user2 = User.objects.create_user(username="raman", password="pass2")

    # Create sweet
    sweet = Sweet.objects.create(name="Gulab Jamun", price=30, quantity=20)

    # Create order for user1
    order_res = APIClient()
    order_res.force_authenticate(user=user1)
    order_res.post("/api/orders/", {
        "items": [{"sweet": sweet.id, "quantity": 2}]
    }, format="json")

    # Now login as user2
    client.force_authenticate(user=user2)
    res = client.get("/api/orders/")

    assert res.status_code == 200
    assert len(res.json()) == 0  # user2 must not see user1's orders


@pytest.mark.django_db
def test_admin_sees_all_orders():
    """Admin user should see all orders in system."""
    client = APIClient()

    # Create admin
    admin = User.objects.create_superuser(
        username="admin", password="admin123", email="admin@example.com"
    )
    client.force_authenticate(user=admin)

    # Create sweet
    sweet = Sweet.objects.create(name="Kaju Katli", price=100, quantity=50)

    # Create an order as a normal user
    normal = User.objects.create_user(username="n1", password="pass")
    normal_client = APIClient()
    normal_client.force_authenticate(user=normal)
    normal_client.post("/api/orders/", {
        "items": [{"sweet": sweet.id, "quantity": 1}]
    }, format="json")

    # Admin list orders
    res = client.get("/api/orders/")

    assert res.status_code == 200
    assert len(res.json()) == 1
