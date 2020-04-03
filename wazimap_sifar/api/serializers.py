from rest_framework import serializers

from wazimap_sifar.models import DatasetCategory, Contributor, Dataset
from django.contrib.auth.models import User


class ContributerSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field="name", queryset=DatasetCategory.objects.all()
    )

    class Meta:
        model = Contributor
        fields = "__all__"


class DatasetCategorySerializer(serializers.ModelSerializer):
    contributer_set = ContributerSerializer(read_only=True, many=True)

    class Meta:
        model = DatasetCategory
        fields = "__all__"


class DatasetSerializer(serializers.ModelSerializer):
    contributer = serializers.SlugRelatedField(
        slug_field="subcategory", queryset=Contributor.objects.all()
    )

    class Meta:
        model = Dataset
        fields = "__all__"
        # exclude = ("latitude", "longitude")
