from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from wazimap_sifar.models import (CommunityPark, DistrictPark,
                                  HealthFacilities, Library, PrivatePharmacy,
                                  ProfessionalService)
from wazimap_sifar.import_resource import (
    CommunityParkResource, DistrictParkResource, LibraryResource,
    PrivatePharmacyResource)


class PrivatePharmacyAdmin(ImportExportModelAdmin):
    resource_class = PrivatePharmacyResource
    search_fields = ['name']
    list_display = ('name', 'organization_unit', 'organization_unit_type',
                    'geo_levels')


class CommunityParkAdmin(ImportExportModelAdmin):
    resource_class = CommunityParkResource
    search_fields = ['name', 'address', 'suburb']
    list_display = ('name', 'suburb', 'geo_levels')


class DistrictParkAdmin(ImportExportModelAdmin):
    resource_class = DistrictParkResource
    search_fields = ['name', 'address', 'suburb']
    list_display = ('name', 'suburb', 'geo_levels')


class LibraryAdmin(ImportExportModelAdmin):
    resource_class = LibraryResource
    search_fields = ['name', 'library_type']
    list_display = ('name', 'members', 'library_type', 'geo_levels')


class HealthFacilitiesAdmin(admin.ModelAdmin):
    list_display = ('name', 'settlement', 'unit', 'geo_levels')


class ProfessionalServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'surname', 'profession', 'geo_levels')


admin.site.register(PrivatePharmacy, PrivatePharmacyAdmin)
admin.site.register(HealthFacilities, HealthFacilitiesAdmin)
admin.site.register(ProfessionalService, ProfessionalServiceAdmin)
admin.site.register(Library, LibraryAdmin)
admin.site.register(CommunityPark, CommunityParkAdmin)
admin.site.register(DistrictPark, DistrictParkAdmin)
