from django.conf.urls import url, patterns, include

from wazimap import urls
from django.contrib import admin

from .api import views as api


urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(
        r'^api/point/v1/sifar/private-pharmacies$',
        api.PrivatePharmacyView.as_view(),
        name='private_pharmacies'),
)

urlpatterns += urls.urlpatterns
