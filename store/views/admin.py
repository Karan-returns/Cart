from rest_framework.response import Response
from rest_framework.views import APIView

from store.permissions import AdminAPIKeyPermission
from store.services.discount_service import DiscountService
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
