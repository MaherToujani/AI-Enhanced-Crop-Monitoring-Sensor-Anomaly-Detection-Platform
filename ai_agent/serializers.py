from rest_framework import serializers

from .models import AgentRecommendation


class AgentRecommendationSerializer(serializers.ModelSerializer):
    plot_name = serializers.CharField(
        source="anomaly_event.plot.name", read_only=True
    )
    farm_name = serializers.CharField(
        source="anomaly_event.plot.farm.name", read_only=True
    )
    anomaly_type = serializers.CharField(
        source="anomaly_event.anomaly_type", read_only=True
    )
    severity = serializers.CharField(
        source="anomaly_event.severity", read_only=True
    )

    class Meta:
        model = AgentRecommendation
        fields = [
            "id",
            "anomaly_event",
            "plot_name",
            "farm_name",
            "anomaly_type",
            "severity",
            "recommended_action",
            "explanation_text",
            "confidence",
            "timestamp",
        ]



