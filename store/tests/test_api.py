from rest_framework import status
from rest_framework.test import APITestCase

from store.tests.base import StoreTestCase


class APIIntegrationTests(StoreTestCase, APITestCase):
    def test_full_purchase_flow(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 1)

        response = self.client.post(
            "/api/carts/alice/items/",
            {"product_id": "prod-1", "quantity": 2},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get("/api/carts/alice/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["subtotal"], "59.98")

        response = self.client.post(
            "/api/checkout/",
            {"customer_id": "alice"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["order"]["total"], "59.98")

    def test_admin_stats_requires_key(self):
        response = self.client.get("/api/admin/stats/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(
            "/api/admin/stats/",
            HTTP_X_ADMIN_KEY="test-admin-key",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("revenue", response.json())

    def test_admin_generate_discount_at_milestone(self):
        for i in range(3):
            self.client.post(
                f"/api/carts/user{i}/items/",
                {"product_id": "prod-1", "quantity": 1},
                format="json",
            )
            self.client.post(
                "/api/checkout/",
                {"customer_id": f"user{i}"},
                format="json",
            )

        response = self.client.post(
            "/api/admin/discount-codes/generate/",
            HTTP_X_ADMIN_KEY="test-admin-key",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("code", response.json())
