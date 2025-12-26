from rest_framework import serializers

from .models import SensorReading


class SensorReadingSerializer(serializers.ModelSerializer):
    plot_name = serializers.CharField(source="plot.name", read_only=True)
    farm_name = serializers.CharField(source="plot.farm.name", read_only=True)

    class Meta:
        model = SensorReading
        fields = [
            "id",
            "plot",
            "plot_name",
            "farm_name",
            "timestamp",
            "sensor_type",
            "value",
            "source",
            "created_at",
        ]



