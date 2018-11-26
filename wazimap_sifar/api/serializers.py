from rest_framework import serializers

from wazimap_sifar.models import PrivatePharmacy


class PrivatePharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivatePharmacy
        exclude = ('facility', 'id')
