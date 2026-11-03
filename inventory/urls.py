from django.urls import path
from .views import asset_list

urlpatterns = [
    path("", asset_list, name="asset-list"),
]
