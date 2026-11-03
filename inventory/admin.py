from django.contrib import admin
from .models import Asset

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("name", "asset_type", "ip_address", "status", "created_at")
    list_filter = ("asset_type", "status")
    search_fields = ("name", "ip_address")
