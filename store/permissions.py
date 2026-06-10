from django.conf import settings
from rest_framework.permissions import BasePermission


class AdminAPIKeyPermission(BasePermission):
    message = "Invalid or missing admin API key."

    def has_permission(self, request, view):
        api_key = request.headers.get("X-Admin-Key", "")
        return api_key == settings.ADMIN_API_KEY
