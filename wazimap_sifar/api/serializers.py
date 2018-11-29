from rest_framework import serializers

from wazimap_sifar.models import (
    CommunityPark, DistrictPark, HealthFacilities,
    Library, PrivatePharmacy, ProfessionalService)


class PrivatePharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivatePharmacy
        exclude = ('id', )


class CommunityParkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityPark
        exclude = ('id', )


class DistrictParkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistrictPark
        exclude = ('id', )


class HealthFacilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthFacilities
        exclude = ('id', )


class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        exclude = ('id', )


class ProfessionalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalService
        exclude = ('id', )
