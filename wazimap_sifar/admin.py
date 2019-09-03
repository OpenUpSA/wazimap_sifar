import sys

reload(sys)
sys.setdefaultencoding("utf8")

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from wazimap_sifar.models import Dataset, DatasetCategory, Contributer
from wazimap_sifar.resource import DatasetResource
from wazimap_sifar.forms import CustomImportForm, CustomConfirmImportForm
from django import forms
from django.contrib.gis import forms as gis_form


class DatasetForm(forms.ModelForm):
    point = gis_form.PointField(
        required=True,
        srid=4326,
        widget=gis_form.OSMWidget(
            attrs={
                "map_width": 800,
                "map_height": 500,
                "default_lat": "-28.556",
                "default_lon": "23.879",
                "default_zoom": "20",
            }
        ),
    )

    def clean(self):
        data = super(DatasetForm, self).clean()
        point = data.get("point")
        if not point:
            raise forms.ValidationError("Select a location")

        self.instance.latitude = point.x
        self.instance.longitude = point.y
        return data


class DatasetAdmin(ImportExportModelAdmin):
    form = DatasetForm
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
    readonly_fields = ("latitude", "longitude")

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
