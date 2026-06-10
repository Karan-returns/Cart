from rest_framework.response import Response
from rest_framework.views import APIView

from store.serializers import CheckoutSerializer
from store.services.checkout_service import CheckoutService


class CheckoutPreviewView(APIView):
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = CheckoutService().preview_checkout(
            customer_id=serializer.validated_data["customer_id"],
            discount_code=serializer.validated_data.get("discount_code"),
        )
        return Response(result)


class CheckoutView(APIView):
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = CheckoutService().checkout(
            customer_id=serializer.validated_data["customer_id"],
            discount_code=serializer.validated_data.get("discount_code"),
        )
        return Response(result, status=201)
