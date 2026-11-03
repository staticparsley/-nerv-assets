from django.test import TestCase
from django.urls import reverse

from .models import Asset


class AssetAPITests(TestCase):
    def setUp(self):
        self.asset = Asset.objects.create(
            name="Beelink EQ13",
            asset_type=Asset.AssetType.COMPUTE,
            status=Asset.Status.ACTIVE,
            ip_address="192.168.1.100",
        )

    def test_asset_list_returns_assets(self):
        response = self.client.get(reverse("asset-list"))

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data["assets"]), 1)
        self.assertEqual(data["assets"][0]["name"], "Beelink EQ13")
        self.assertEqual(data["assets"][0]["asset_type"], "compute")

    def test_asset_list_empty_database(self):
        Asset.objects.all().delete()

        response = self.client.get(reverse("asset-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"assets": []})
