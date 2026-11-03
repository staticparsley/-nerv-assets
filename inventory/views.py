from django.shortcuts import render
from django.http import JsonResponse
from .models import Asset

def asset_list(request):
    assets = Asset.objects.all()

    data = [
        {
            "id": asset.id,
            "name": asset.name,
            "asset_type": asset.asset_type,
            "ip_address": asset.ip_address,
            "status": asset.status,
        }
        for asset in assets
    ]

    return JsonResponse({"assets": data})
