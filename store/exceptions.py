from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


class StoreError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A store error occurred."

    def __init__(self, detail=None):
        self.detail = detail or self.default_detail


class ProductNotFoundError(StoreError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Product not found."


class CartEmptyError(StoreError):
    default_detail = "Cart is empty."


class InvalidQuantityError(StoreError):
    default_detail = "Quantity must be greater than zero."


class InvalidDiscountCodeError(StoreError):
    default_detail = "Invalid or already used discount code."


class DiscountGenerationError(StoreError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Discount code cannot be generated at this time."


def custom_exception_handler(exc, context):
    if isinstance(exc, StoreError):
        return Response({"detail": exc.detail}, status=exc.status_code)

    return exception_handler(exc, context)
