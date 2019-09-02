import sys

reload(sys)
sys.setdefaultencoding("utf8")

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from wazimap_sifar.models import Dataset, DatasetCategory, Contributer
from wazimap_sifar.resource import DatasetResource
from wazimap_sifar.forms import CustomImportForm, CustomConfirmImportForm


class DatasetAdmin(ImportExportModelAdmin):
    resource_class = DatasetResource
    list_display = (
        "name",
        "address",
        "latitude",
        "longitude",
        "email",
        "website",
        "phone_number",
        "contributer",
    )
    exclude = ("type",)
    search_fields = ("name",)
    list_filter = ("contributer__subcategory",)

    def get_import_form(self):
        return CustomImportForm

    def get_confirm_input_form():
        return CustomConfirmImportForm

    def get_resource_kwargs(self, request, *args, **kwargs):
        rk = super(DatasetAdmin, self).get_resource_kwargs(request, *args, **kwargs)
        rk["contributer"] = None
        if request.POST:
            contributer = request.POST.get("contributer", None)
            if contributer:
                request.session["contributer"] = contributer
            else:
                try:
                    # If we don't have it from a form field, we should find it in the session.
                    contributer = request.session["contributer"]
                except KeyError as e:
                    raise Exception("Context failure on row import, " + e)
            rk["contributer"] = contributer
        return rk


class ContributerAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "subcategory", "approved")


admin.site.register(Dataset, DatasetAdmin)
admin.site.register(DatasetCategory)
admin.site.register(Contributer, ContributerAdmin)
