import time

import requests

from django.core.management.base import BaseCommand, CommandError
from wazimap_sifar.models import PrivatePharmacy


class Command(BaseCommand):
    help = "Search and find in which geographies a point belongs to"

    def add_arguments(self, parser):
        parser.add_argument(
            '--model', action='store', dest='model', default='PrivatePharmacy')
        parser.add_argument(
            '--mapit', action='store', dest='mapit',
            default='https://mapit.code4sa.org/point/4326/')

    def handle(self, *args, **options):
        """
        Get the district geo code from mapit based on the faclities lat/lon
        """
        try:
            model = eval(options.get('model'))
            for facility in model.objects.all():
                codes = []
                lat = facility.latitude
                lon = facility.longitude
                url = options.get(
                    'mapit') + '{},{}?type=PR,DC,MN&generation=1'.format(
                        lon, lat)
                req = requests.get(url)
                geo = req.json()
                if geo:
                    for _, value in geo.items():
                        codes.append(value['codes']['MDB'])
                    facility.geo_levels = codes
                    facility.save(update_fields=['geo_levels'])
                    self.stdout.write(self.style.SUCCESS("Geo Inserted"))
                else:
                    self.stdout.write(self.style.ERROR("No Parent Found"))
                time.sleep(1)
        except Exception as error:
            raise CommandError(error)
