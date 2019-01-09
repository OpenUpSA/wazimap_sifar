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

    def handle(self, *args, **options):
        if not options.get('store'):
            raise CommandError("Subplace csv file needed")
        with open(options.get('store')) as csv_file:
            try:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    obj, created = Geography.update_or_create(
                        {
                            'version': 2011,
                            'geo_code': row['SP_CODE'],
                            'geo_level': 'sub-place',
                            'name': row['SP_NAME'],
                            'parent_level': 'municipality',
                            'parent_code': row['MN_MDB_C']
                        },
                        geo_code=row['SP_CODE'])
                    self.stdout.write(self.style.SUCCESS('Sub-place added'))
            except Exception as error:
                self.stdout.write(self.style.ERROR('%s' % error))
                raise
