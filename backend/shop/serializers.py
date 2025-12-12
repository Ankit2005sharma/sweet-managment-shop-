from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Sweet

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Return public user fields."""

    class Meta:
        model = User
        fields = ("id", "username", "email")


class RegisterSerializer(serializers.ModelSerializer):
    """Create user with hashed password."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data.get("email", "")
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class SweetSerializer(serializers.ModelSerializer):
    """Serialize Sweet model."""

    class Meta:
        model = Sweet
        fields = ("id", "name", "price", "quantity")
