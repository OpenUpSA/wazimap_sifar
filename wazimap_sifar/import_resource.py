from django.core.exceptions import ValidationError
from import_export.fields import Field as BaseField
from import_export.resources import ModelResource

from wazimap_sifar.models import Library, PrivatePharmacy


class FieldWithDBValidation(BaseField):

    empty_values = [None, '', 'NULL']

    def __init__(self, model, *args, **kwargs):
        self.model = model
        super(FieldWithDBValidation, self).__init__(*args, **kwargs)

    def clean(self, data):
        value = super(FieldWithDBValidation, self).clean(data)
        try:
            model_field = self.model._meta.get_field(self.attribute)
            model_field.validate(value, None)
        except ValidationError as e:
            raise ValueError("Column '%s': %s" % (self.column_name, e))
        return value


def field_factory(model):
    def inner(*args, **kwargs):
        field = FieldWithDBValidation(model, *args, **kwargs)
        return field
    return inner


class BaseResource(ModelResource):

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        required_fields = {f.column_name for f in self.fields.values()}
        fields_in_file = set(dataset.headers)
        missing_fields = required_fields - fields_in_file
        if missing_fields:
            raise ValueError('Missing headers: %s' % list(missing_fields))


class PrivatePharmacyResource(BaseResource):
    Field = field_factory(PrivatePharmacy)
    province = Field(attribute='province', column_name='Province')
    district = Field(attribute='district', column_name='District')
    sub_district = Field(attribute='sub_district', column_name='Sub-District')
    facility = Field(attribute='facility', column_name='Facility')
    latitude = Field(attribute='latitude', column_name='Latitude')
    longitude = Field(attribute='longitude', column_name='Longitude')
    organization_unit = Field(
        attribute='organization_unit',
        column_name='Organization Unit Rural_Urban_Semi')
    organization_unit_type = Field(
        attribute='organization_unit_type',
        column_name='Organization Unit Type')
    address = Field(attribute='address', column_name='Physical Address')

    class Meta:
        model = PrivatePharmacy
        import_id_fields = PrivatePharmacy._meta.unique_together[0]
        fields = [
            'province',
            'district',
            'sub_district',
            'facility',
            'latitude',
            'longitude',
            'organization_unit',
            'organization_unit_type',
            'address',
        ]


class LibraryResource(BaseResource):
    Field = field_factory(Library)
    name = Field(attribute='name', column_name='Name', default='')
    members = Field(attribute='members', column_name='Members', default=None)
    library_type = Field(attribute='library_type', column_name='Type')
    longitude = Field(attribute='longitude', column_name='XCoord')
    latitude = Field(attribute='latitude', column_name='YCoord')

    class Meta:
        model = Library
        import_id_fields = Library._meta.unique_together[0]
        fields = [
            'name',
            'members',
            'library_type',
            'latitude',
            'longitude',
        ]
