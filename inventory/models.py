from django.db import models

class Asset(models.Model):

    class AssetType(models.TextChoices):
        COMPUTE = "compute", "Compute"
        NETWORK = "network", "Network"
        STORAGE = "storage", "Storage"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PLANNED = "planned", "Planned"
        OFFLINE = "offline", "Offline"

    name = models.CharField(max_length=100)
    asset_type = models.CharField(
            max_length=20,
            choices=AssetType.choices,
    )
    ip_address = models.GenericIPAddressField(
            null=True,
            blank=True,
    )
    status = models.CharField(
            max_length=20,
            choices=Status.choices,
            default=Status.PLANNED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

