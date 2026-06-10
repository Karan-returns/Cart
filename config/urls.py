from django.urls import include, path

from store.views.ui import AdminDashboardView, ShopView

urlpatterns = [
    path("", ShopView.as_view(), name="shop"),
    path("admin/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("api/", include("store.urls")),
]
