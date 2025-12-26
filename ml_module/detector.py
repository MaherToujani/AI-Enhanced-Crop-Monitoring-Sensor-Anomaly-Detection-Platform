from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Optional

import pandas as pd

from farms.models import FieldPlot
from ml_module.models import AnomalyEvent
from sensors.models import SensorReading


"""
Threshold-based anomaly detection for sensor readings.
Defines normal ranges per sensor type and flags readings outside these bounds.
"""


SensorType = Literal["moisture", "temperature", "humidity"]


@dataclass
class DetectionResult:
    is_anomaly: bool
    anomaly_type: Optional[str] = None
    severity: Optional[str] = None
    confidence: float = 0.0
    details: Optional[dict] = None


class ThresholdAnomalyDetector:
    """
    Very simple rule-based detector using the indicative ranges from the subject:

    - Soil moisture normal: 45–75%
      * Sudden drop or value < 35 → irrigation_issue
    - Temperature normal: 18–28°C
      * >32°C → heat_stress
      * <10°C → cold_stress
    - Humidity normal: 45–75%
      * <30 or >85 → general_anomaly (environmental)
    """

    # Normal ranges
    MOISTURE_MIN = 45
    MOISTURE_MAX = 75
    MOISTURE_LOW_PERSISTENT = 35

    TEMP_MIN = 18
    TEMP_MAX = 28
    TEMP_HOT = 32
    TEMP_COLD = 10

    HUM_MIN = 45
    HUM_MAX = 75
    HUM_LOW = 30
    HUM_HIGH = 85

    def detect(self, reading: SensorReading) -> DetectionResult:
        """Detect anomalies in a sensor reading using threshold or statistical analysis."""
        sensor_type: SensorType = reading.sensor_type  # type: ignore[assignment]
        value = float(reading.value)

        recent_readings = self._get_recent_readings(reading.plot, sensor_type, reading.timestamp)
        if recent_readings:
            df = pd.DataFrame(recent_readings)
            mean_value = df['value'].mean()
            std_value = df['value'].std()
            
            if sensor_type == SensorReading.SENSOR_TYPE_MOISTURE:
                return self._detect_moisture_with_context(reading.plot, value, mean_value, std_value)
            if sensor_type == SensorReading.SENSOR_TYPE_TEMPERATURE:
                return self._detect_temperature_with_context(value, mean_value, std_value)
            if sensor_type == SensorReading.SENSOR_TYPE_HUMIDITY:
                return self._detect_humidity_with_context(value, mean_value, std_value)
        if sensor_type == SensorReading.SENSOR_TYPE_MOISTURE:
            return self._detect_moisture(reading.plot, value)
        if sensor_type == SensorReading.SENSOR_TYPE_TEMPERATURE:
            return self._detect_temperature(value)
        if sensor_type == SensorReading.SENSOR_TYPE_HUMIDITY:
            return self._detect_humidity(value)

        return DetectionResult(is_anomaly=False)
    
    def _get_recent_readings(self, plot: FieldPlot, sensor_type: str, timestamp, hours: int = 24) -> Optional[list]:
        """Get recent readings for statistical context analysis."""
        from datetime import timedelta
        from django.utils import timezone
        
        cutoff = timestamp - timedelta(hours=hours)
        readings = SensorReading.objects.filter(
            plot=plot,
            sensor_type=sensor_type,
            timestamp__gte=cutoff,
            timestamp__lt=timestamp
        ).order_by('timestamp')[:50]
        
        if readings.count() < 5:
            return None
        
        return [{'timestamp': r.timestamp, 'value': float(r.value)} for r in readings]
    
    def _detect_moisture_with_context(self, plot: FieldPlot, value: float, mean: float, std: float) -> DetectionResult:
        """Moisture detection using statistical context (z-score)."""
        z_score = abs((value - mean) / std) if std > 0 else 0
        
        if value < self.MOISTURE_LOW_PERSISTENT:
            return DetectionResult(
                is_anomaly=True,
                anomaly_type=AnomalyEvent.ANOMALY_IRRIGATION,
                severity=AnomalyEvent.SEVERITY_HIGH,
                confidence=0.9,
                details={"reason": "moisture_below_35", "value": value, "z_score": z_score},
            )
        
        if z_score > 2.0:
            return DetectionResult(
                is_anomaly=True,
                anomaly_type=AnomalyEvent.ANOMALY_IRRIGATION,
                severity=AnomalyEvent.SEVERITY_MEDIUM,
                confidence=0.75,
                details={"reason": "statistical_anomaly", "value": value, "z_score": z_score, "mean": mean},
            )
        
        return self._detect_moisture(plot, value)
    
    def _detect_temperature_with_context(self, value: float, mean: float, std: float) -> DetectionResult:
        """Temperature detection using statistical context."""
        z_score = abs((value - mean) / std) if std > 0 else 0
        
        if value > self.TEMP_HOT or (z_score > 2.5 and value > mean):
            return DetectionResult(
                is_anomaly=True,
                anomaly_type=AnomalyEvent.ANOMALY_HEAT_STRESS,
                severity=AnomalyEvent.SEVERITY_HIGH,
                confidence=0.9,
                details={"reason": "temperature_anomaly", "value": value, "z_score": z_score},
            )
        
        if value < self.TEMP_COLD or (z_score > 2.5 and value < mean):
            return DetectionResult(
                is_anomaly=True,
                anomaly_type=AnomalyEvent.ANOMALY_COLD_STRESS,
                severity=AnomalyEvent.SEVERITY_MEDIUM,
                confidence=0.8,
                details={"reason": "temperature_anomaly", "value": value, "z_score": z_score},
            )
        
        return self._detect_temperature(value)
    
    def _detect_humidity_with_context(self, value: float, mean: float, std: float) -> DetectionResult:
        """Humidity detection using statistical context."""
        z_score = abs((value - mean) / std) if std > 0 else 0
        
        if (value < self.HUM_LOW or value > self.HUM_HIGH) or z_score > 2.0:
            return DetectionResult(
                is_anomaly=True,
                anomaly_type=AnomalyEvent.ANOMALY_GENERAL,
                severity=AnomalyEvent.SEVERITY_MEDIUM,
                confidence=0.7,
                details={"reason": "humidity_anomaly", "value": value, "z_score": z_score},
            )
        
        return self._detect_humidity(value)

    def _detect_moisture(self, plot: FieldPlot, value: float) -> DetectionResult:
        if value < self.MOISTURE_LOW_PERSISTENT:
            return DetectionResult(
                is_anomaly=True,
                anomaly_type=AnomalyEvent.ANOMALY_IRRIGATION,
                severity=AnomalyEvent.SEVERITY_HIGH,
                confidence=0.9,
                details={
                    "reason": "moisture_below_35",
                    "value": value,
                    "threshold": self.MOISTURE_LOW_PERSISTENT,
                },
            )

        if value < self.MOISTURE_MIN:
            return DetectionResult(
                is_anomaly=True,
                anomaly_type=AnomalyEvent.ANOMALY_IRRIGATION,
                severity=AnomalyEvent.SEVERITY_MEDIUM,
                confidence=0.7,
                details={
                    "reason": "moisture_below_normal_range",
                    "value": value,
                    "range": [self.MOISTURE_MIN, self.MOISTURE_MAX],
                },
            )

        if value > self.MOISTURE_MAX:
            return DetectionResult(
                is_anomaly=True,
                anomaly_type=AnomalyEvent.ANOMALY_GENERAL,
                severity=AnomalyEvent.SEVERITY_LOW,
                confidence=0.6,
                details={
                    "reason": "moisture_above_normal_range",
                    "value": value,
                    "range": [self.MOISTURE_MIN, self.MOISTURE_MAX],
                },
            )

        return DetectionResult(is_anomaly=False, confidence=0.9)

    def _detect_temperature(self, value: float) -> DetectionResult:
        if value > self.TEMP_HOT:
            return DetectionResult(
                is_anomaly=True,
                anomaly_type=AnomalyEvent.ANOMALY_HEAT_STRESS,
                severity=AnomalyEvent.SEVERITY_HIGH,
                confidence=0.9,
                details={
                    "reason": "temperature_above_32",
                    "value": value,
                    "threshold": self.TEMP_HOT,
                },
            )

        if value < self.TEMP_COLD:
            return DetectionResult(
                is_anomaly=True,
                anomaly_type=AnomalyEvent.ANOMALY_COLD_STRESS,
                severity=AnomalyEvent.SEVERITY_MEDIUM,
                confidence=0.8,
                details={
                    "reason": "temperature_below_10",
                    "value": value,
                    "threshold": self.TEMP_COLD,
                },
            )

        return DetectionResult(is_anomaly=False, confidence=0.9)

    def _detect_humidity(self, value: float) -> DetectionResult:
        if value < self.HUM_LOW or value > self.HUM_HIGH:
            return DetectionResult(
                is_anomaly=True,
                anomaly_type=AnomalyEvent.ANOMALY_GENERAL,
                severity=AnomalyEvent.SEVERITY_MEDIUM,
                confidence=0.7,
                details={
                    "reason": "humidity_outside_extreme_bounds",
                    "value": value,
                    "extremes": [self.HUM_LOW, self.HUM_HIGH],
                },
            )

        return DetectionResult(is_anomaly=False, confidence=0.9)


def create_anomaly_for_reading(reading: SensorReading) -> Optional[AnomalyEvent]:
    """Run detector and create AnomalyEvent if anomaly is detected."""
    detector = ThresholdAnomalyDetector()
    result = detector.detect(reading)

    if not result.is_anomaly:
        return None

    anomaly = AnomalyEvent.objects.create(
        plot=reading.plot,
        sensor_reading=reading,
        timestamp=reading.timestamp,
        anomaly_type=result.anomaly_type or AnomalyEvent.ANOMALY_GENERAL,
        severity=result.severity or AnomalyEvent.SEVERITY_LOW,
        model_confidence=result.confidence,
        details=result.details or {},
    )
    return anomaly



