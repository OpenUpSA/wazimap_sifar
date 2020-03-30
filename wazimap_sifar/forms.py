from django import forms
from import_export.forms import ImportForm, ConfirmImportForm
from wazimap_sifar.models import Contributor


class CustomImportForm(ImportForm):
    contributer = forms.ModelChoiceField(
        queryset=Contributor.objects.all(), required=True
    )


class CustomConfirmImportForm(ConfirmImportForm):
    contributer = forms.ModelChoiceField(
        queryset=Contributor.objects.all(), required=True
    )
