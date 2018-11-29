from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from wazimap_sifar.models import (
    HealthFacilities, Library, PrivatePharmacy, ProfessionalService)
from wazimap_sifar.import_resource import (
    LibraryResource, PrivatePharmacyResource)


class PrivatePharmacyAdmin(ImportExportModelAdmin):
    resource_class = PrivatePharmacyResource
    search_fields = ['facility']


class LibraryAdmin(ImportExportModelAdmin):
    resource_class = LibraryResource
    search_fields = ['name', 'library_type']


class HealthFacilitiesAdmin(admin.ModelAdmin):
    list_display = ('name', )


class ProfessionalServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'surname', 'profession')


admin.site.register(PrivatePharmacy, PrivatePharmacyAdmin)
admin.site.register(HealthFacilities, HealthFacilitiesAdmin)
admin.site.register(ProfessionalService, ProfessionalServiceAdmin)
admin.site.register(Library, LibraryAdmin)
