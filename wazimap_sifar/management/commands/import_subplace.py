import csv

from django.core.management.base import BaseCommand, CommandError
from wazimap.models import Geography
"""
Script to import subplaces to wazimap
"""


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'filepath', action='store', help='File containing sub-places')

    def handle(self, *args, **kwargs):
        if not kwargs['filepath']:
            raise CommandError("Subplace csv file needed")
        with open(kwargs['filepath']) as csv_file:
            try:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    obj, created = Geography.objects.update_or_create(
                        {
                            'version': 2016,
                            'geo_code': row['SP_CODE'],
                            'geo_level': 'subplace',
                            'name': row['SP_NAME'],
                            'parent_level': 'municipality',
                            'parent_code': row['MN_MDB_C']
                        },
                        geo_code=row['SP_CODE'])
                    self.stdout.write(self.style.SUCCESS('Sub-place added'))
            except Exception as error:
                self.stdout.write(self.style.ERROR('%s' % error))
                raise
