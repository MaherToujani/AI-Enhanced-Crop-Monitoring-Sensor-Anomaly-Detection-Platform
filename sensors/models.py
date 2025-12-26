from django.db import models

from farms.models import FieldPlot


class SensorReading(models.Model):
    """
    Single sensor measurement for a given plot and time.

    Simple and extendable: we can add more sensor types later without
    changing the overall design.
    """

    SENSOR_TYPE_MOISTURE = "moisture"
    SENSOR_TYPE_TEMPERATURE = "temperature"
    SENSOR_TYPE_HUMIDITY = "humidity"

    SENSOR_TYPE_CHOICES = [
        (SENSOR_TYPE_MOISTURE, "Soil moisture"),
        (SENSOR_TYPE_TEMPERATURE, "Air temperature"),
        (SENSOR_TYPE_HUMIDITY, "Air humidity"),
    ]

    SOURCE_SIMULATOR = "simulator"
    SOURCE_REAL = "real_sensor"

    SOURCE_CHOICES = [
        (SOURCE_SIMULATOR, "Simulator"),
        (SOURCE_REAL, "Real sensor"),
    ]

    plot = models.ForeignKey(
        FieldPlot,
        on_delete=models.CASCADE,
        related_name="sensor_readings",
    )
    timestamp = models.DateTimeField()
    sensor_type = models.CharField(
        max_length=20,
        choices=SENSOR_TYPE_CHOICES,
    )
    value = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        help_text="Raw sensor value (units depend on sensor type).",
    )
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default=SOURCE_SIMULATOR,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["plot", "timestamp"]),
            models.Index(fields=["sensor_type", "timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.sensor_type}={self.value} at {self.timestamp} ({self.plot})"
