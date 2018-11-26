from rest_framework import serializers

from wazimap_sifar.models import PrivatePharmacy, HealthFacilities, ProfessionalService


class PrivatePharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivatePharmacy
        exclude = ('id', )


class HealthFacilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthFacilities
        exclude = ('id', )


class ProfessionalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalService
        exclude = ('id', )
