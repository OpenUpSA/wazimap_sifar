from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from wazimap_sifar.models import (
    CommunityPark, DistrictPark, HealthFacilities,
    Library, PrivatePharmacy, ProfessionalService)
from . import serializers


class GenericPointView(APIView):
    """
    Get all the points within a particular geography
    """
    model = None
    model_serializer = None

    def get(self, request):
        self.geo_code = request.query_params.get('geo_code', None)
        if self.geo_code:
            query = self.model\
                    .objects\
                    .filter(geo_levels__overlap=[self.geo_code])
            serialize = self.model_serializer(query, many=True)
            return Response({'data': serialize.data})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class PrivatePharmacyView(GenericPointView):
    model = PrivatePharmacy
    model_serializer = serializers.PrivatePharmacySerializer


class HealthFacilitiesView(GenericPointView):
    model = HealthFacilities
    model_serializer = serializers.HealthFacilitiesSerializer


class CommunityParkView(GenericPointView):
    model = CommunityPark
    model_serializer = serializers.CommunityParkSerializer


class DistrictParkView(GenericPointView):
    model = DistrictPark
    model_serializer = serializers.DistrictParkSerializer


class LibraryView(GenericPointView):
    model = Library
    model_serializer = serializers.LibrarySerializer


class ProfessionalServiceView(GenericPointView):
    model = ProfessionalService
    model_serializer = serializers.ProfessionalServiceSerializer
