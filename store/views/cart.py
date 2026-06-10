from rest_framework.response import Response
from rest_framework.views import APIView

from store.serializers import AddCartItemSerializer
from store.services.cart_service import CartService


class CartDetailView(APIView):
    def get(self, request, customer_id):
        cart = CartService().get_cart(customer_id)
        return Response(cart)


class CartAddItemView(APIView):
    def post(self, request, customer_id):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = CartService().add_item(
            customer_id=customer_id,
            product_id=serializer.validated_data["product_id"],
            quantity=serializer.validated_data["quantity"],
        )
        return Response(
            {
                "customer_id": cart.customer_id,
                "item_count": len(cart.items),
                "message": "Item added to cart.",
            },
            status=201,
        )
