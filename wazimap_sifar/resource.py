from import_export import resources

from wazimap_sifar.models import Dataset


class DatasetResource(resources.ModelResource):
    def __init__(self, contributer=None):
        super(DatasetResource, self)
        self.contributer = contributer

    def before_import_row(self, row, **kwargs):
        row['contributer'] = self.contributer

    class Meta:
        model = Dataset
        import_id_fields = ('name', )
        exclude = ('id', )
