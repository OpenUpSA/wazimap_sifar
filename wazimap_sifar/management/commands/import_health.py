import csv

from django.core.management.base import BaseCommand, CommandError
from wazimap_sifar import models


class Command(BaseCommand):
    help = "Load the various health facilities"

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)
        parser.add_argument('dataset', type=str)
        parser.add_argument('--profession', type=str)

    def handle(self, *args, **kwargs):

        if kwargs['file'] is None or kwargs['dataset'] is None:
            raise CommandError("File and Dataset needed")
        if kwargs['dataset'] == 'private_pharmacies':
            code_prefix = 'PPF'
        elif kwargs['dataset'] == 'public_health':
            code_prefix = 'PHF'
        elif kwargs['dataset'] == 'marie_stopes':
            code_prefix = 'MSS'
        elif kwargs['dataset'] == 'profession':
            code_prefix = 'PS'
        else:
            raise CommandError('Uknown dataset')

        try:
            with open(kwargs['file'], 'r') as data_file:
                reader = csv.DictReader(data_file)
                if kwargs['dataset'] == 'private_pharmacies':
                    health_facilities.pharmacies(reader, code_prefix)
                elif kwargs['dataset'] == 'public_health':
                    public_facilities(reader, code_prefix)
                elif kwargs['dataset'] == 'marie_stopes':
                    health_facilities.marie_stopes(reader, code_prefix)
                elif kwargs['dataset'] == 'profession':
                    professional_service(reader, code_prefix,
                                         kwargs['profession'])
                else:
                    raise CommandError("Unknown Dataset")
        except Exception as error:
            raise CommandError(error)


def public_facilities(reader, code_prefix):
    code = 0
    for row in reader:
        row.pop('Province')
        row.pop('District')
        row.pop('Sub-District')
        row.pop('Facility Name 1')
        models.HealthFacilities\
            .objects\
            .update_or_create(
                {
                    'name': row.pop('Facility Name_2'),
                    'settlement': row.pop('Organization Unit Rural_Urban_Semi'),
                    'unit': row.pop('Organization Unit Type'),
                    'latitude': row.pop('Latitude'),
                    'longitude': row.pop('Longitude'),
                    'facility_code': '{}{}'.format(code_prefix, code),
                    'dataset': 'public_health',
                    'service': dict(row)
                },
                facility_code='{}{}'.format(code_prefix, code)
            )
        code += 1
        print("Facility Entered")
    print(code)


def professional_service(reader, code_prefix, profession):
    code = 0
    for row in reader:
        models.ProfessionalService\
            .objects\
            .update_or_create(
                {
                    'title': row.pop('title'),
                    'name': row.pop('firstname'),
                    'surname': row.pop('lastname'),
                    'latitude': row.pop('Latitude'),
                    'longitude': row.pop('Longitude'),
                    'service_code': '{}{}'.format(code_prefix, code),
                    'profession': profession,
                    'details': dict(row)
                },
                service_code='{}{}'.format(code_prefix, code)
            )
        code += 1
        print("Professional Added")
    print(code)


def pharmacies(reader, code_prefix):
    code = 5084
    for row in reader:
        row.pop('Province')
        row.pop('District')
        row.pop('Sub-District')
        models.PrivatePharmacy\
            .objects\
            .update_or_create(
                {
                    'name': row.pop('Facility'),
                    'settlement': row.pop('Organization Unit Rural_Urban_Semi'),
                    'latitude': row.pop('Latitude'),
                    'longitude': row.pop('Longitude'),
                    'unit': row.pop('Organization Unit Type'),
                    'address': row.pop('Physical Address'),
                    'dataset': 'private_pharmacies',
                    'facility_code': '{}{}'.format(code_prefix, code),
                    'service': dict(row)
                },
                facility_code='{}{}'.format(code_prefix, code)
            )
        code += 1
        print("Facility Entered")
    print(code)
