from __future__ import unicode_literals

from django.db import models

from django.contrib.postgres.fields import ArrayField, HStoreField


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
        db_table = 'private_pharmacy'
        unique_together = ('facility', 'latitude', 'longitude',
                           'organization_unit_type')

    def __unicode__(self):
        return '%s, %s' % (self.facility, self.organization_unit_type)


class HealthFacilities(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    settlement = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    facility_code = models.CharField(max_length=20, unique=True)
    geo_levels = ArrayField(
        models.CharField(max_length=20), blank=True, null=True)
    dataset = models.CharField(max_length=50)
    service = HStoreField()

    class Meta:
        db_table = 'health_facilities'
        unique_together = ('name', 'latitude', 'longitude', 'facility_code')

    def __str__(self):
        return self.name


class Library(models.Model):
    name = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    library_type = models.CharField(max_length=100, blank=True)
    members = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'library'
        unique_together = ('name', 'latitude', 'longitude', 'library_type')

    def __str__(self):
        return self.name


class ProfessionalService(models.Model):
    title = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    service_code = models.CharField(max_length=20)
    profession = models.CharField(max_length=100)
    geo_levels = ArrayField(
        models.CharField(max_length=20), blank=True, null=True)
    details = HStoreField()

    class Meta:
        db_table = 'professional_service'

    def __str__(self):
        return '{} {} {}'.format(self.title, self.name, self.surname)
