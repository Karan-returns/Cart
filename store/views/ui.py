from django.conf import settings
from django.views.generic import TemplateView


class ShopView(TemplateView):
    template_name = "store/shop.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "shop"
        context["discount_every_n"] = settings.DISCOUNT_EVERY_N_ORDERS
        context["discount_percent"] = settings.DISCOUNT_PERCENT
        return context


class AdminDashboardView(TemplateView):
    template_name = "store/admin.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "admin"
        context["discount_every_n"] = settings.DISCOUNT_EVERY_N_ORDERS
        context["discount_percent"] = settings.DISCOUNT_PERCENT
        return context
