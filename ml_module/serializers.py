from rest_framework import serializers

from .models import AnomalyEvent


class AnomalyEventSerializer(serializers.ModelSerializer):
    plot_name = serializers.CharField(source="plot.name", read_only=True)
    farm_name = serializers.CharField(source="plot.farm.name", read_only=True)

    class Meta:
        model = AnomalyEvent
        fields = [
            "id",
            "plot",
            "plot_name",
            "farm_name",
            "sensor_reading",
            "timestamp",
            "anomaly_type",
            "severity",
            "model_confidence",
            "details",
            "created_at",
        ]



