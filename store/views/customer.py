from rest_framework.response import Response
from rest_framework.views import APIView

from store.services.customer_service import CustomerService


class CustomerProfileView(APIView):
    def get(self, request, customer_id):
        return Response(CustomerService().get_profile(customer_id))
