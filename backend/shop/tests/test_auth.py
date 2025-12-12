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
    })

    assert res.status_code == 201

    # Login user
    res2 = client.post("/api/auth/login/", {
        "username": "ankit",
        "password": "TestPass123!"
    })

    assert res2.status_code == 200
    assert "access" in res2.json()
    assert "refresh" in res2.json()
