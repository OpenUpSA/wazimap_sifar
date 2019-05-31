import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.serializers import serialize as geo_serialize

from wazimap_sifar.models import DatasetCategory, Contributer, Dataset
from . import serializers
from wazimap_sifar.utils import to_geojson


class DatasetCategoryView(APIView):
    model = DatasetCategory
    model_serializer = serializers.DatasetCategorySerializer

    def get(self, request):
        query = self.model.objects.all()
        serialize = self.model_serializer(query, many=True)
        return Response({'data': serialize.data})


class DatasetContributers(APIView):
    def get(self, request, contrib_id):
        data = to_geojson(Dataset)
        return Response(data)
