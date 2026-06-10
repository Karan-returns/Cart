from django.urls import path

from store.views.admin import AdminGenerateDiscountView, AdminStatsView
from store.views.cart import CartAddItemView, CartDetailView
from store.views.checkout import CheckoutView
from store.views.products import ProductListView

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("carts/<str:customer_id>/", CartDetailView.as_view(), name="cart-detail"),
    path(
        "carts/<str:customer_id>/items/",
        CartAddItemView.as_view(),
        name="cart-add-item",
    ),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path(
        "admin/discount-codes/generate/",
        AdminGenerateDiscountView.as_view(),
        name="admin-generate-discount",
    ),
    path("admin/stats/", AdminStatsView.as_view(), name="admin-stats"),
]
