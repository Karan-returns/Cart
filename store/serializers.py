from rest_framework import serializers


class AddCartItemSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1)


class CheckoutSerializer(serializers.Serializer):
    customer_id = serializers.CharField()
    discount_code = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_discount_code(self, value):
        return value.strip() or None


class ProductSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    price = serializers.CharField()


class AdminSettingsSerializer(serializers.Serializer):
    discount_every_n_orders = serializers.IntegerField(min_value=1, required=False)
    discount_percent = serializers.IntegerField(min_value=1, max_value=100, required=False)
    discount_code_prefix = serializers.CharField(max_length=20, required=False)
