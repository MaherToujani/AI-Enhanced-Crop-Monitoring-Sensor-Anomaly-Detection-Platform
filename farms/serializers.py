from rest_framework import serializers

from .models import FarmProfile, FieldPlot


class FieldPlotSerializer(serializers.ModelSerializer):
    farm_name = serializers.SerializerMethodField()

    class Meta:
        model = FieldPlot
        fields = [
            "id",
            "farm",
            "farm_name",
            "name",
            "crop_variety",
            "area_hectares",
            "created_at",
            "updated_at",
        ]

    def get_farm_name(self, obj):
        return obj.farm.name if obj.farm else None


class FarmProfileSerializer(serializers.ModelSerializer):
    plots = FieldPlotSerializer(many=True, read_only=True)

    class Meta:
        model = FarmProfile
        fields = [
            "id",
            "owner",
            "name",
            "location",
            "size_hectares",
            "crop_type",
            "created_at",
            "updated_at",
            "plots",
        ]
        read_only_fields = ["owner", "created_at", "updated_at", "plots"]



