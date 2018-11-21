from django.conf.urls import url, patterns, include

from wazimap import urls
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += urls.urlpatterns
