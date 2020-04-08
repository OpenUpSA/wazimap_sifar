from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class DatasetCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "sifar_dataset_category"
        verbose_name_plural = "Dataset Categories"

    def __str__(self):
        return self.name


class Contributor(models.Model):
    user = models.ForeignKey(User)
    category = models.ForeignKey(
        DatasetCategory,
        on_delete=models.CASCADE,
        null=True,
        related_name="contributors",
    )
    subcategory = models.CharField(max_length=255)
    approved = models.BooleanField(default=False)

    class Meta:
        db_table = "sifar_contributers"
        unique_together = ("category", "subcategory")

    def __str__(self):
        return self.subcategory


class Dataset(models.Model):
    contributer = models.ForeignKey(
        Contributor, on_delete=models.CASCADE, null=True, verbose_name="Contributor"
    )
    name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "sifar_dataset"
        unique_together = (
            "address",
            "name",
            "latitude",
            "longitude",
            "contributer",
            "email",
            "website",
            "phone_number",
        )

    def __str__(self):
        return self.contributer.subcategory
