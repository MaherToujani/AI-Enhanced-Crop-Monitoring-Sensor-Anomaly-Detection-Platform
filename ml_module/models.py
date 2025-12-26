from django.db import models

from farms.models import FieldPlot
from sensors.models import SensorReading


class AnomalyEvent(models.Model):
    """
    Represents a detected anomaly for a given plot and (optionally) sensor reading.

    The ML module will create these records. The schema is intentionally simple
    so we can plug in different models later without changing the DB structure.
    """

    ANOMALY_IRRIGATION = "irrigation_issue"
    ANOMALY_HEAT_STRESS = "heat_stress"
    ANOMALY_COLD_STRESS = "cold_stress"
    ANOMALY_SENSOR = "sensor_malfunction"
    ANOMALY_GENERAL = "general_anomaly"

    ANOMALY_TYPE_CHOICES = [
        (ANOMALY_IRRIGATION, "Irrigation issue"),
        (ANOMALY_HEAT_STRESS, "Heat stress"),
        (ANOMALY_COLD_STRESS, "Cold stress"),
        (ANOMALY_SENSOR, "Sensor malfunction"),
        (ANOMALY_GENERAL, "General anomaly"),
    ]

    SEVERITY_LOW = "low"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_HIGH = "high"

    SEVERITY_CHOICES = [
        (SEVERITY_LOW, "Low"),
        (SEVERITY_MEDIUM, "Medium"),
        (SEVERITY_HIGH, "High"),
    ]

    plot = models.ForeignKey(
        FieldPlot,
        on_delete=models.CASCADE,
        related_name="anomalies",
    )
    sensor_reading = models.ForeignKey(
        SensorReading,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="anomalies",
        help_text="Reading that triggered this anomaly (if applicable).",
    )
    timestamp = models.DateTimeField(
        help_text="Time when the anomaly was detected.",
    )
    anomaly_type = models.CharField(
        max_length=50,
        choices=ANOMALY_TYPE_CHOICES,
        default=ANOMALY_GENERAL,
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default=SEVERITY_LOW,
    )
    model_confidence = models.FloatField(
        help_text="Confidence score from the ML model (0.0–1.0).",
    )
    details = models.JSONField(
        blank=True,
        null=True,
        help_text="Optional JSON field for extra model details/context.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.anomaly_type} ({self.severity}) on {self.plot} at {self.timestamp}"
