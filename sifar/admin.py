from django.contrib import admin
from import_export.admin import ImportMixin, ImportExportModelAdmin

from sifar.models import PrivatePharmacy
from sifar.import_resource import PrivatePharmacyResource


class PrivatePharmacyAdmin(ImportExportModelAdmin):
    resource_class = PrivatePharmacyResource
    search_fields = ['facility']


admin.site.register(PrivatePharmacy, PrivatePharmacyAdmin)
