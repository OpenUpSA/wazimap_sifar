from django import forms
from import_export.forms import ImportForm, ConfirmImportForm
from wazimap_sifar.models import Contributer


class CustomImportForm(ImportForm):
    contributer = forms.ModelChoiceField(
        queryset=Contributer.objects.all(), required=True)


class CustomConfirmImportForm(ConfirmImportForm):
    contributer = forms.ModelChoiceField(
        queryset=Contributer.objects.all(), required=True)
