from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..models import Sweet
from ..serializers import SweetSerializer


@api_view(["GET", "POST"])
def sweets_view(request):
    """List sweets or create a new sweet (admin only)."""

    if request.method == "GET":
        sweets = Sweet.objects.all()
        return Response(SweetSerializer(sweets, many=True).data, status=200)

    # POST → admin-only creation
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
    """Purchase a sweet and reduce stock."""
    try:
        sweet = Sweet.objects.get(pk=pk)
    except Sweet.DoesNotExist:
        return Response({"error": "Sweet not found"}, status=404)

    amount = int(request.data.get("amount", 0))

    if amount <= 0:
        return Response({"error": "Invalid amount"}, status=400)

    if sweet.quantity < amount:
        return Response({"error": "Not enough quantity"}, status=400)

    sweet.quantity -= amount
    sweet.save()

    return Response(
        {"remaining_quantity": sweet.quantity},
        status=200
    )
