
import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_user_register_and_login():
    client = APIClient()

    # Register user
    res = client.post("/api/auth/register/", {
        "username": "ankit",
        "password": "TestPass123!",
        "email": "ankit@example.com"
    }, format="json")

    assert res.status_code == 201

    # Login user
    res2 = client.post("/api/auth/login/", {
        "username": "ankit",
        "password": "TestPass123!"
    }, format="json")

    assert res2.status_code == 200
    data = res2.json()
    assert "access" in data
    assert "refresh" in data
