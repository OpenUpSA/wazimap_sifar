from __future__ import unicode_literals

from django.db import models

from django.contrib.postgres.fields import ArrayField


class PrivatePharmacy(models.Model):
    province = models.CharField(blank=True, max_length=100)
    district = models.CharField(blank=True, max_length=100)
    sub_district = models.CharField(blank=True, max_length=100)
    facility = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=200, blank=True)
    organization_unit = models.CharField(max_length=200, blank=True)
    organization_unit_type = models.CharField(max_length=200, blank=True)
    geo_levels = ArrayField(
        models.CharField(max_length=20), blank=True, null=True)

    # settlement = models.CharField(max_length=100, blank=True)
    # unit = models.CharField(max_length=50, blank=True)
    # facility_code = models.CharField(max_length=20, unique=True)
    # dataset = models.CharField(max_length=50)
    # service = HStoreField()

    class Meta:
        verbose_name_plural = 'private pharmacies'
        db_table = 'private_pharmacies'
        unique_together = (
            'facility', 'latitude', 'longitude', 'organization_unit_type')

    def __unicode__(self):
        return '%s, %s' % (self.facility, self.organization_unit_type)
