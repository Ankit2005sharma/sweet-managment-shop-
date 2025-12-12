from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Sweet, Order, OrderItem

User = get_user_model()


# ---------------------------------------------------------
#   EXISTING AUTH SERIALIZERS (unchanged)
# ---------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class RegisterSerializer(serializers.ModelSerializer):
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


# ---------------------------------------------------------
#   SWEET (existing)
# ---------------------------------------------------------

class SweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sweet
        fields = ("id", "name", "price", "quantity")


# ---------------------------------------------------------
#   NEW ORDER SERIALIZERS FOR GREEN TEST PASS
# ---------------------------------------------------------

class OrderCreateItemSerializer(serializers.Serializer):
    """Used when creating an order"""
    sweet = serializers.IntegerField()
    quantity = serializers.IntegerField()


class OrderItemSerializer(serializers.ModelSerializer):
    """Used when returning orders"""
    sweet = SweetSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ("sweet", "quantity")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ("id", "total_price", "items", "created_at")

    def get_total_price(self, obj):
        return int(obj.total_price)

