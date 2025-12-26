from django.db.models.signals import post_save
from django.dispatch import receiver

from ml_module.detector import create_anomaly_for_reading
from .models import SensorReading


@receiver(post_save, sender=SensorReading)
def run_threshold_detector_on_new_reading(
    sender, instance: SensorReading, created: bool, **kwargs
):
    """
    When a new SensorReading is created, run the simple threshold-based detector.

    If an anomaly is detected, an AnomalyEvent will be created automatically.
    """

    if not created:
        return

    create_anomaly_for_reading(instance)



