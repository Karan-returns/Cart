from django.urls import path

from store.views.admin import (
    AdminCustomerDetailView,
    AdminCustomersView,
    AdminGenerateDiscountView,
    AdminSettingsView,
    AdminStatsView,
)
from store.views.cart import CartAddItemView, CartDetailView
from store.views.checkout import CheckoutPreviewView, CheckoutView
from store.views.customer import CustomerProfileView
from store.views.products import ProductListView

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path(
        "customers/<str:customer_id>/profile/",
        CustomerProfileView.as_view(),
        name="customer-profile",
    ),
    path("carts/<str:customer_id>/", CartDetailView.as_view(), name="cart-detail"),
    path(
        "carts/<str:customer_id>/items/",
        CartAddItemView.as_view(),
        name="cart-add-item",
    ),
    path("checkout/preview/", CheckoutPreviewView.as_view(), name="checkout-preview"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path(
        "admin/discount-codes/generate/",
        AdminGenerateDiscountView.as_view(),
        name="admin-generate-discount",
    ),
    path("admin/stats/", AdminStatsView.as_view(), name="admin-stats"),
    path("admin/customers/", AdminCustomersView.as_view(), name="admin-customers"),
    path(
        "admin/customers/<str:customer_id>/",
        AdminCustomerDetailView.as_view(),
        name="admin-customer-detail",
    ),
    path("admin/settings/", AdminSettingsView.as_view(), name="admin-settings"),
]
