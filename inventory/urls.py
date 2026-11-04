from django.urls import path
from .views import asset_list, asset_detail

urlpatterns = [
    path("", asset_list, name="asset-list"),
    path("<int:asset_id>/", asset_detail, name="asset-detail"),
]
