from __future__ import unicode_literals

from django.db import models

from django.contrib.postgres.fields import ArrayField, HStoreField


class GeoItem(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    geo_levels = ArrayField(
        models.CharField(max_length=20), blank=True, null=True)

    class Meta:
        abstract = True


class PrivatePharmacy(GeoItem):
    province = models.CharField(blank=True, max_length=100)
    district = models.CharField(blank=True, max_length=100)
    sub_district = models.CharField(blank=True, max_length=100)
    facility = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True)
    organization_unit = models.CharField(max_length=200, blank=True)
    organization_unit_type = models.CharField(max_length=200, blank=True)

    # settlement = models.CharField(max_length=100, blank=True)
    # unit = models.CharField(max_length=50, blank=True)
    # facility_code = models.CharField(max_length=20, unique=True)
    # dataset = models.CharField(max_length=50)
    # service = HStoreField()

    class Meta:
        verbose_name_plural = 'private pharmacies'
        db_table = 'private_pharmacy'
        unique_together = ('facility', 'latitude', 'longitude',
                           'organization_unit_type')

    def __unicode__(self):
        return '%s, %s' % (self.facility, self.organization_unit_type)


class HealthFacilities(GeoItem):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True)
    settlement = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    facility_code = models.CharField(max_length=20, unique=True)
    dataset = models.CharField(max_length=50)
    service = HStoreField()

    class Meta:
        db_table = 'health_facilities'
        unique_together = ('name', 'latitude', 'longitude', 'facility_code')

    def __str__(self):
        return self.name


class Library(GeoItem):
    name = models.CharField(max_length=100, blank=True)
    members = models.IntegerField(blank=True, null=True)
    library_type = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name_plural = 'libraries'
        db_table = 'library'
        unique_together = ('name', 'latitude', 'longitude', 'library_type')

    def __str__(self):
        return self.name


class CommunityPark(GeoItem):
    name = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=100, blank=True)
    suburb = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'community_parks'
        unique_together = ('name', 'suburb')

    def __str__(self):
        return self.name


class DistrictPark(GeoItem):
    name = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=100, blank=True)
    suburb = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'distirct_parks'
        unique_together = ('name', 'suburb')

    def __str__(self):
        return self.name


class ProfessionalService(GeoItem):
    title = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    service_code = models.CharField(max_length=20)
    profession = models.CharField(max_length=100)
    details = HStoreField()

    class Meta:
        db_table = 'professional_service'

    def __str__(self):
        return '{} {} {}'.format(self.title, self.name, self.surname)
