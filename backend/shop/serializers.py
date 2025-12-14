from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Sweet, Order


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'password', 'role')
        extra_kwargs = {
            'first_name': {'required': True},
            'username': {'required': True},
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            role=validated_data.get('role', 'user')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class SweetSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.first_name', read_only=True)
    
    class Meta:
        model = Sweet
        fields = ('id', 'name', 'description', 'price', 'quantity', 'category', 'image', 
                 'created_at', 'updated_at', 'created_by', 'created_by_name')
        read_only_fields = ('created_at', 'updated_at', 'created_by')
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value
    
    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    sweet_name = serializers.CharField(source='sweet.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'user', 'user_email', 'sweet', 'sweet_name', 'quantity', 'total_price', 'created_at')
        read_only_fields = ('user', 'total_price', 'created_at')


class PurchaseSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(default=1, min_value=1)


class RestockSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)