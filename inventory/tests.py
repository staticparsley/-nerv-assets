from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

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

    def test_create_asset(self):
        self.authenticate_staff()

        initial_count = Asset.objects.count()

        response = self.client.post(
            "/api/assets/",
            data={
                "name": "Raspberry Pi 5",
                "asset_type": "compute",
                "status": "planned",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Asset.objects.count(), initial_count + 1)

        created_asset = Asset.objects.get(pk=response.json()["id"])
        self.assertEqual(created_asset.name, "Raspberry Pi 5")
    

    def test_create_asset_without_name(self):
        self.authenticate_staff()
        initial_count = Asset.objects.count()

        response = self.client.post(
                "/api/assets/",
                data={
                    "asset_type": "compute",
                    "status": "planned",
                },
                content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Asset.objects.count(), initial_count)

    
    def test_get_asset_detail(self):
        asset = Asset.objects.create(
            name="NERV Test Node",
            asset_type="compute",
            status="active",
        )

        response = self.client.get(f"/api/assets/{asset.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "NERV Test Node")


    def test_update_asset(self):
        self.authenticate_staff()
        asset = Asset.objects.create(
            name="Raspberry Pi 5",
            asset_type="compute",
            status="planned",
        )

        response = self.client.patch(
            f"/api/assets/{asset.id}/",
            data={"status": "active"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        asset.refresh_from_db()
        self.assertEqual(asset.status, "active")


    def test_invalid_asset_update(self):
        self.authenticate_staff()
        asset = Asset.objects.create(
            name="Test Node",
            asset_type="compute",
            status="planned",
        )

        response = self.client.patch(
            f"/api/assets/{asset.id}/",
            data={"status": "banana"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

        asset.refresh_from_db()
        self.assertEqual(asset.status, "planned")


    def test_delete_asset(self):
        self.authenticate_staff()
        asset = Asset.objects.create(
            name="Temporary Node",
            asset_type="compute",
            status="planned",
        )

        response = self.client.delete(f"/api/assets/{asset.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Asset.objects.filter(pk=asset.id).exists())


    def test_get_missing_asset(self):
        response = self.client.get("/api/assets/999999/")

        self.assertEqual(response.status_code, 404)

    def authenticate_staff(self):
        User = get_user_model()

        user = User.objects.create_user(
            username="nerv-test-admin",
            password="test-password",
            is_staff=True,
        )

        self.client.force_login(user)

    def test_anonymous_user_can_list_assets(self):
        response = self.client.get("/api/assets/")

        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_canot_create_assets(self):
        response = self.client.post(
            "/api/assets/",
            data={"name": "Unauthorized Node"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertFalse(
            Asset.objects.filter(name="Unauthorized Node").exists()
        )

    def test_non_staff_user_cannot_delete_asset(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="regular=user",
            password="test-password",
        )

        self.client.force_login(user)

        asset = Asset.objects.create(
            name="Protected Node",
            asset_type="compute",
            status="active",
        )

        response = self.client.delete(f"/api/assets/{asset.id}/")

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Asset.objects.filter(pk=asset.id).exists())
