from django.test import SimpleTestCase, TestCase
from django.urls import reverse

class HealthTests(SimpleTestCase):
    def test_healthz(self):
        response = self.client.get(reverse("healthz"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class ReadinessTests(TestCase):
    def test_readyz(self):
        response = self.client.get(reverse("readyz"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ready"})
