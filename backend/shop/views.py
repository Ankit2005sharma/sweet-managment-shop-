from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer,
    UserSerializer,
    SweetSerializer
)
from .models import Sweet


# ---------------------------
# AUTH REGISTRATION VIEW
# ---------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    """Register a new user and return minimal profile details."""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

## LOG IN VIEW

@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """
    Authenticate user and return JWT tokens (access + refresh).
    """
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({"error": "Invalid credentials"}, status=400)

    # Create JWT tokens
    refresh = RefreshToken.for_user(user)
    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "username": user.username
    }, status=200)
    
# ---------------------------
# SWEETS VIEWS
# ---------------------------

@api_view(["GET", "POST"])
def sweets_view(request):
    """List sweets or create a new sweet (admin only)."""

    # GET → list sweets
    if request.method == "GET":
        sweets = Sweet.objects.all()
        return Response(SweetSerializer(sweets, many=True).data, status=200)

    # POST → admin-only create
    if not request.user.is_staff:
        return Response({"detail": "Forbidden"}, status=403)

    serializer = SweetSerializer(data=request.data)
    if serializer.is_valid():
        sweet = serializer.save()
        return Response(SweetSerializer(sweet).data, status=201)

    return Response(serializer.errors, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def purchase_sweet(request, pk):
    """Purchase a sweet and reduce quantity."""
    try:
        sweet = Sweet.objects.get(pk=pk)
    except Sweet.DoesNotExist:
        return Response({"error": "Sweet not found"}, status=404)

    amount = int(request.data.get("amount", 0))

    if amount <= 0:
        return Response({"error": "Invalid amount"}, status=400)

    if sweet.quantity < amount:
        return Response({"error": "Not enough quantity"}, status=400)

    # Reduce inventory
    sweet.quantity -= amount
    sweet.save()

    return Response({"remaining_quantity": sweet.quantity}, status=200)
