from django.conf.urls import url, include

from wazimap import urls
from django.contrib import admin

from .api import views as api

urlpatterns = [
    url(r"^admin/", include(admin.site.urls)),
    url(
        "^api/v1/dataset/category$", api.DatasetCategoryView.as_view(), name="category"
    ),
    url(
        "^api/v1/dataset/contributer$",
        api.ContributerView.as_view(),
        name="contributer",
    ),
    url(
        "^api/v1/dataset/contributer/(?P<contrib_id>[0-9]+)$",
        api.DatasetContributers.as_view(),
        name="contributer",
    ),
    url("^api/v1/dataset/datasets$", api.DatasetView.as_view(), name="datasets"),
    url("^explorer/", include("explorer.urls", namespace="explorer")),
]

urlpatterns += urls.urlpatterns
