import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_list_sweets_empty():
    """Initially, the sweets list should be empty."""
    client = APIClient()
    res = client.get("/api/sweets/")
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.django_db
def test_create_sweet_admin_only():
    """Only admin can create sweets."""
    client = APIClient()

    # normal user
    user = User.objects.create_user(username="ankit", password="testpass123")
    client.force_authenticate(user=user)

    res = client.post("/api/sweets/", {
        "name": "Barfi",
        "price": 50,
        "quantity": 10
    }, format="json")

    assert res.status_code == 403  # Forbidden for non-admin users

    # admin user
    admin = User.objects.create_superuser(
        username="admin", password="adminpass123", email="admin@x.com"
    )
    client.force_authenticate(user=admin)

    res = client.post("/api/sweets/", {
        "name": "Barfi",
        "price": 50,
        "quantity": 10
    }, format="json")

    assert res.status_code == 201
    assert res.json()["name"] == "Barfi"


@pytest.mark.django_db
def test_purchase_sweet_reduces_quantity():
    """Purchasing a sweet must reduce quantity."""
    client = APIClient()

    # create admin
    admin = User.objects.create_superuser(username="admin", password="adminpass", email="admin@example.com")
    client.force_authenticate(user=admin)

    # create sweet
    res = client.post("/api/sweets/", {
        "name": "Ladoo",
        "price": 10,
        "quantity": 5
    }, format="json")
    sweet_id = res.json()["id"]

    # login as user
    user = User.objects.create_user(username="ankit", password="testpass")
    client.force_authenticate(user=user)

    # purchase
    res = client.post(f"/api/sweets/{sweet_id}/purchase/", {
        "amount": 2
    }, format="json")

    assert res.status_code == 200
    assert res.json()["remaining_quantity"] == 3


@pytest.mark.django_db
def test_purchase_fails_if_not_enough_quantity():
    """Purchase must fail if quantity is insufficient."""
    client = APIClient()

    # create admin
    admin = User.objects.create_superuser(username="admin", password="adminpass", email="admin@example.com")
    client.force_authenticate(user=admin)

    # create sweet with low stock
    res = client.post("/api/sweets/", {
        "name": "Jalebi",
        "price": 20,
        "quantity": 1
    }, format="json")
    sweet_id = res.json()["id"]

    # login as user
    user = User.objects.create_user(username="ankit", password="testpass")
    client.force_authenticate(user=user)

    # purchase more than available
    res = client.post(f"/api/sweets/{sweet_id}/purchase/", {
        "amount": 5
    }, format="json")

    assert res.status_code == 400
    assert "Not enough quantity" in res.json()["error"]
