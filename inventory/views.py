import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404


from .models import Asset
from .permissions import staff_required_for_writes

@require_http_methods(["GET", "POST"])
@staff_required_for_writes
def asset_list(request):
    if request.method == "GET":
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

    # POST: Create a new asset.
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not isinstance(payload, dict):
        return JsonResponse({"error": "Expected a JSON object"}, status=400)

    name = payload.get("name")
    if not isinstance(name, str) or not name.strip():
        return JsonResponse({"error": "Name is required"}, status=400)

    asset = Asset(
        name=name,
        asset_type=payload.get("asset_type", Asset.AssetType.COMPUTE),
        ip_address=payload.get("ip_address"),
        status=payload.get("status", Asset.Status.PLANNED),
    )

    try:
        asset.full_clean()
    except Exception as exc:
        from django.core.exceptions import ValidationError

        if isinstance(exc, ValidationError):
            return JsonResponse({"errors": exc.message_dict}, status=400)
        raise

    asset.save()

    return JsonResponse(
        {
            "id": asset.id,
            "name": asset.name,
            "asset_type": asset.asset_type,
            "ip_address": asset.ip_address,
            "status": asset.status,
        },
        status=201,
    )


@require_http_methods(["GET", "PATCH", "DELETE"])
@staff_required_for_writes
def asset_detail(request, asset_id):
    asset = get_object_or_404(Asset, pk=asset_id)

    if request.method == "GET":
        return JsonResponse({
            "id": asset.id,
            "name": asset.name,
            "asset_type": asset.asset_type,
            "ip_address": asset.ip_address,
            "status": asset.status,
        })

    if request.method == "DELETE":
        asset.delete()
        return HttpResponse(status=204)

    # PATCH: Update selected fields.
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not isinstance(payload, dict):
        return JsonResponse({"error": "Expected a JSON object"}, status=400)

    allowed_fields = {
        "name", "asset_type", "ip_address", "status"
    }

    unknown_fields = set(payload) - allowed_fields
    if unknown_fields:
        return JsonResponse(
            {"error": f"Unknown fields: {sorted(unknown_fields)}"},
            status=400,
        )

    for field, value in payload.items():
        setattr(asset, field, value)

    try:
        asset.full_clean()
    except ValidationError as exc:
        return JsonResponse({"errors": exc.message_dict}, status=400)

    asset.save()

    return JsonResponse({
        "id": asset.id,
        "name": asset.name,
        "asset_type": asset.asset_type,
        "ip_address": asset.ip_address,
        "status": asset.status,
    })

