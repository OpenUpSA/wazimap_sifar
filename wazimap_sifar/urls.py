from django.conf.urls import url, include

from wazimap import urls
from django.contrib import admin

from .api import views as api

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/point/v1/sifar/private-pharmacies$',
        api.PrivatePharmacyView.as_view(),
        name='private_pharmacies'),
    url(r'^api/point/v1/sifar/health-services$',
        api.HealthFacilitiesView.as_view(),
        name='health_facilities'),
    url(r'^api/point/v1/sifar/community-parks$',
        api.CommunityParkView.as_view(),
        name='libraries'),
    url(r'^api/point/v1/sifar/district-parks$',
        api.DistrictParkView.as_view(),
        name='libraries'),
    url(r'^api/point/v1/sifar/libraries$',
        api.LibraryView.as_view(),
        name='libraries'),
    url(r'^api/point/v1/sifar/professional-services$',
        api.ProfessionalServiceView.as_view(),
        name='professional_service'),
    url('^explorer/', include('explorer.urls', namespace='explorer'))
]

urlpatterns += urls.urlpatterns
