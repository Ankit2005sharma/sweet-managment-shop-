from rest_framework import status, generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
from django.db import transaction

from .models import User, Sweet, Order
from .serializers import (
    UserSerializer, LoginSerializer, SweetSerializer, 
    OrderSerializer, PurchaseSerializer, RestockSerializer
)
from .permissions import IsAdminUser, IsAdminOrReadOnly


# ============= AUTH VIEWS =============

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user.
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.first_name,
                'role': user.role,
                'token': str(refresh.access_token)
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login user and return JWT token.
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(email=email)
            
            # Check password using Django's built-in method
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'name': user.first_name,
                        'role': user.role,
                        'token': str(refresh.access_token)
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============= SWEET VIEWS =============

class SweetListCreateView(generics.ListCreateAPIView):
    """
    GET: List all sweets
    POST: Create a new sweet (Admin only)
    """
    queryset = Sweet.objects.all()
    serializer_class = SweetSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SweetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a sweet
    PUT/PATCH: Update a sweet (Admin only)
    DELETE: Delete a sweet (Admin only)
    """
    queryset = Sweet.objects.all()
    serializer_class = SweetSerializer
    permission_classes = [IsAdminOrReadOnly]


@api_view(['GET'])
@permission_classes([AllowAny])
def search_sweets(request):
    """
    Search sweets by name, category, or price range.
    Query params: name, category, min_price, max_price
    """
    queryset = Sweet.objects.all()
    
    # Search by name
    name = request.query_params.get('name', None)
    if name:
        queryset = queryset.filter(name__icontains=name)
    
    # Filter by category
    category = request.query_params.get('category', None)
    if category:
        queryset = queryset.filter(category=category)
    
    # Filter by price range
    min_price = request.query_params.get('min_price', None)
    max_price = request.query_params.get('max_price', None)
    
    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)
    
    serializer = SweetSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ============= INVENTORY VIEWS =============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def purchase_sweet(request, pk):
    """
    Purchase a sweet, decreasing its quantity.
    """
    try:
        sweet = Sweet.objects.get(pk=pk)
    except Sweet.DoesNotExist:
        return Response({
            'error': 'Sweet not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = PurchaseSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    quantity = serializer.validated_data.get('quantity', 1)
    
    # Check if enough quantity available
    if sweet.quantity < quantity:
        return Response({
            'error': f'Insufficient quantity. Only {sweet.quantity} available.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create order and update quantity in a transaction
    try:
        with transaction.atomic():
            # Decrease quantity
            sweet.quantity -= quantity
            sweet.save()
            
            # Create order
            total_price = sweet.price * quantity
            order = Order.objects.create(
                user=request.user,
                sweet=sweet,
                quantity=quantity,
                total_price=total_price
            )
            
            return Response({
                'message': 'Purchase successful',
                'order': OrderSerializer(order).data,
                'remaining_quantity': sweet.quantity
            }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def restock_sweet(request, pk):
    """
    Restock a sweet, increasing its quantity (Admin only).
    """
    try:
        sweet = Sweet.objects.get(pk=pk)
    except Sweet.DoesNotExist:
        return Response({
            'error': 'Sweet not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = RestockSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    quantity = serializer.validated_data['quantity']
    
    # Increase quantity
    sweet.quantity += quantity
    sweet.save()
    
    return Response({
        'message': 'Restock successful',
        'sweet': SweetSerializer(sweet).data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_orders(request):
    """
    Get all orders for the authenticated user.
    """
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)