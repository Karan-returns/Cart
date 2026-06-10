from rest_framework.response import Response
from rest_framework.views import APIView

from store.permissions import AdminAPIKeyPermission
from store.serializers import AdminSettingsSerializer
from store.services.customer_service import CustomerService
from store.services.discount_service import DiscountService
from store.services.settings_service import SettingsService
from store.services.stats_service import StatsService


class AdminGenerateDiscountView(APIView):
    permission_classes = [AdminAPIKeyPermission]

    def post(self, request):
        discount = DiscountService().generate_code(force=True)
        return Response(
            {
                "code": discount.code,
                "percent": discount.percent,
                "issued_for_order_number": discount.issued_for_order_number,
                "message": "Discount code generated successfully.",
            },
            status=201,
        )


class AdminStatsView(APIView):
    permission_classes = [AdminAPIKeyPermission]

    def get(self, request):
        return Response(StatsService().get_stats())


class AdminCustomersView(APIView):
    permission_classes = [AdminAPIKeyPermission]

    def get(self, request):
        return Response(CustomerService().list_customers())


class AdminCustomerDetailView(APIView):
    permission_classes = [AdminAPIKeyPermission]

    def get(self, request, customer_id):
        return Response(CustomerService().get_customer_detail(customer_id))


class AdminSettingsView(APIView):
    permission_classes = [AdminAPIKeyPermission]

    def get(self, request):
        return Response(SettingsService().get_settings())

    def patch(self, request):
        serializer = AdminSettingsSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(SettingsService().update_settings(**serializer.validated_data))
