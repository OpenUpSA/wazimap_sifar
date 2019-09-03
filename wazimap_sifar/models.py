from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class DatasetCategory(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "sifar_dataset_category"
        verbose_name_plural = "Dataset Categories"

    def __str__(self):
        return self.name


class Contributer(models.Model):
    user = models.ForeignKey(User)
    category = models.ForeignKey(DatasetCategory, on_delete=models.CASCADE, null=True)
    subcategory = models.CharField(max_length=255)
    approved = models.BooleanField(default=False)

    class Meta:
        db_table = "sifar_contributers"

    def __str__(self):
        return self.subcategory


class Dataset(models.Model):
    contributer = models.ForeignKey(
        Contributer, on_delete=models.CASCADE, null=True, verbose_name="Source"
    )
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    class Meta:
        db_table = "sifar_dataset"
        unique_together = ("address", "name", "latitude", "longitude", "contributer")

    def __str__(self):
        return self.contributer.subcategory
