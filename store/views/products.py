from rest_framework.response import Response
from rest_framework.views import APIView

from store.repositories.product_repo import ProductRepository


class ProductListView(APIView):
    def get(self, request):
        products = ProductRepository().list_all()
        data = [
            {"id": p.id, "name": p.name, "price": str(p.price)} for p in products
        ]
        return Response(data)
