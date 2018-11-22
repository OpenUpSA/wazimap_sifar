from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from wazimap_sifar.models import PrivatePharmacy
from wazimap_sifar.import_resource import PrivatePharmacyResource


class PrivatePharmacyAdmin(ImportExportModelAdmin):
    resource_class = PrivatePharmacyResource
    search_fields = ['facility']


admin.site.register(PrivatePharmacy, PrivatePharmacyAdmin)
