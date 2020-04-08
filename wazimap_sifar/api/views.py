import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.serializers import serialize as geo_serialize

from wazimap_sifar.models import DatasetCategory, Contributor, Dataset
from . import serializers
from wazimap_sifar.utils import to_geojson


class DatasetCategoryView(APIView):
    model = DatasetCategory
    model_serializer = serializers.DatasetCategorySerializer

    def get(self, request):
        query = self.model.objects.all()
        serialize = self.model_serializer(query, many=True)
        return Response({"data": serialize.data})

    def post(self, request):
        serializer = self.model_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContributerView(APIView):
    model = Contributor
    model_serializer = serializers.ContributerSerializer

    def get(self, request):
        query = self.model.objects.all()
        serialize = self.model_serializer(query, many=True)
        return Response({"data": serialize.data})

    def post(self, request):
        serializer = self.model_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DatasetView(APIView):
    model = Dataset
    model_serializer = serializers.DatasetSerializer

    def get(self, request):
        query = self.model.objects.all()
        serialize = self.model_serializer(query, many=True)
        return Response({"data": serialize.data})

    def post(self, request):
        serializer = self.model_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
