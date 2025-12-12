from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from ..models import Order, OrderItem, Sweet
from ..serializers import OrderSerializer, OrderCreateItemSerializer


@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def orders_view(request):
    user = request.user

    # GET — list orders
    if request.method == "GET":
        if user.is_staff:
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=user)

        return Response(OrderSerializer(orders, many=True).data)

    # POST — create order
    items_data = request.data.get("items", [])
    create_serializer = OrderCreateItemSerializer(data=items_data, many=True)

    if not create_serializer.is_valid():
        return Response(create_serializer.errors, status=400)

    order = Order.objects.create(user=user)

    total_price = 0

    for item in create_serializer.validated_data:
        sweet_id = item["sweet"]
        qty = item["quantity"]

        try:
            sweet = Sweet.objects.get(id=sweet_id)
        except Sweet.DoesNotExist:
            return Response({"error": "Sweet not found"}, status=404)

        if sweet.quantity < qty:
            return Response({"error": "Not enough quantity"}, status=400)

        # reduce stock
        sweet.quantity -= qty
        sweet.save()

        # add order item
        OrderItem.objects.create(order=order, sweet=sweet, quantity=qty)
        total_price += sweet.price * qty

    order.total_price = total_price
    order.save()

    return Response(OrderSerializer(order).data, status=201)
