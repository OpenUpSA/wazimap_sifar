from rest_framework import serializers

from wazimap_sifar.models import DatasetCategory, Contributor, Dataset


class ContributerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = "__all__"


class DatasetCategorySerializer(serializers.ModelSerializer):
    contributer_set = ContributerSerializer(read_only=True, many=True)

    class Meta:
        model = DatasetCategory
        fields = "__all__"
