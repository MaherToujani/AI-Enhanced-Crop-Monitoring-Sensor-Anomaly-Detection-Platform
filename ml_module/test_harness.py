"""
Test Harness for ML Model Evaluation

This module provides a test harness that generates synthetic sensor data
with known anomaly labels (ground truth) for evaluating the ML model.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from decimal import Decimal

import numpy as np

from django.utils import timezone
from django.contrib.auth import get_user_model

from farms.models import FarmProfile, FieldPlot
from sensors.models import SensorReading
from ml_module.evaluation import AnomalyEvaluator, EvaluationMetrics, print_evaluation_report

User = get_user_model()


class SyntheticDataGenerator:
    """Generates synthetic sensor data with known anomalies for testing."""

    def __init__(self, plot: FieldPlot, num_readings: int = 100):
        self.plot = plot
        self.num_readings = num_readings
        self.ground_truth: Dict[int, Tuple[bool, str]] = {}

    def generate_normal_reading(self, timestamp: datetime) -> SensorReading:
        """Generate a normal sensor reading."""
        moisture = Decimal(str(np.random.normal(60.0, 10.0)))
        temperature = Decimal(str(np.random.normal(23.0, 3.0)))
        humidity = Decimal(str(np.random.normal(60.0, 10.0)))

        reading = SensorReading.objects.create(
            plot=self.plot,
            timestamp=timestamp,
            sensor_type=SensorReading.SENSOR_TYPE_MOISTURE,
            value=moisture,
            source=SensorReading.SOURCE_SIMULATOR,
        )
        self.ground_truth[reading.id] = (False, None)

        reading = SensorReading.objects.create(
            plot=self.plot,
            timestamp=timestamp,
            sensor_type=SensorReading.SENSOR_TYPE_TEMPERATURE,
            value=temperature,
            source=SensorReading.SOURCE_SIMULATOR,
        )
        self.ground_truth[reading.id] = (False, None)

        reading = SensorReading.objects.create(
            plot=self.plot,
            timestamp=timestamp,
            sensor_type=SensorReading.SENSOR_TYPE_HUMIDITY,
            value=humidity,
            source=SensorReading.SOURCE_SIMULATOR,
        )
        self.ground_truth[reading.id] = (False, None)

        return reading

    def generate_anomaly_reading(
        self, timestamp: datetime, anomaly_type: str
    ) -> SensorReading:
        """Generate an anomalous sensor reading."""
        reading = None

        if anomaly_type == "irrigation_issue":
            moisture = Decimal(str(np.random.uniform(10.0, 35.0)))
            reading = SensorReading.objects.create(
                plot=self.plot,
                timestamp=timestamp,
                sensor_type=SensorReading.SENSOR_TYPE_MOISTURE,
                value=moisture,
                source=SensorReading.SOURCE_SIMULATOR,
            )
            self.ground_truth[reading.id] = (True, "irrigation_issue")

        elif anomaly_type == "heat_stress":
            temperature = Decimal(str(np.random.uniform(32.0, 40.0)))
            reading = SensorReading.objects.create(
                plot=self.plot,
                timestamp=timestamp,
                sensor_type=SensorReading.SENSOR_TYPE_TEMPERATURE,
                value=temperature,
                source=SensorReading.SOURCE_SIMULATOR,
            )
            self.ground_truth[reading.id] = (True, "heat_stress")

        elif anomaly_type == "cold_stress":
            temperature = Decimal(str(np.random.uniform(5.0, 10.0)))
            reading = SensorReading.objects.create(
                plot=self.plot,
                timestamp=timestamp,
                sensor_type=SensorReading.SENSOR_TYPE_TEMPERATURE,
                value=temperature,
                source=SensorReading.SOURCE_SIMULATOR,
            )
            self.ground_truth[reading.id] = (True, "cold_stress")

        elif anomaly_type == "humidity_anomaly":
            if np.random.random() < 0.5:
                humidity = Decimal(str(np.random.uniform(10.0, 30.0)))
            else:
                humidity = Decimal(str(np.random.uniform(85.0, 95.0)))
            
            reading = SensorReading.objects.create(
                plot=self.plot,
                timestamp=timestamp,
                sensor_type=SensorReading.SENSOR_TYPE_HUMIDITY,
                value=humidity,
                source=SensorReading.SOURCE_SIMULATOR,
            )
            self.ground_truth[reading.id] = (True, "general_anomaly")

        return reading

    def generate_test_dataset(
        self, anomaly_ratio: float = 0.2
    ) -> Tuple[List[SensorReading], Dict[int, Tuple[bool, str]]]:
        """
        Generate a test dataset with known anomalies.
        
        Args:
            anomaly_ratio: Ratio of readings that should be anomalies (0.0-1.0)
        
        Returns:
            Tuple of (list of readings, ground truth dictionary)
        """
        readings = []
        base_time = timezone.now() - timedelta(hours=self.num_readings)

        num_anomalies = int(self.num_readings * anomaly_ratio)
        anomaly_types = ["irrigation_issue", "heat_stress", "cold_stress", "humidity_anomaly"]

        # Generate readings
        for i in range(self.num_readings):
            timestamp = base_time + timedelta(minutes=i * 15)  # Every 15 minutes

            if i < num_anomalies:
                anomaly_type = np.random.choice(anomaly_types)
                reading = self.generate_anomaly_reading(timestamp, anomaly_type)
                if reading:
                    readings.append(reading)
            else:
                # Generate normal reading
                reading = self.generate_normal_reading(timestamp)
                readings.append(reading)

        return readings, self.ground_truth


def run_evaluation_test(plot: FieldPlot, num_readings: int = 100, anomaly_ratio: float = 0.2):
    """
    Run a complete evaluation test.
    
    Args:
        plot: FieldPlot to use for testing
        num_readings: Number of readings to generate
        anomaly_ratio: Ratio of readings that should be anomalies
    
    Returns:
        EvaluationMetrics object
    """
    print(f"\n🧪 Running Evaluation Test")
    print(f"   Plot: {plot.name}")
    print(f"   Readings: {num_readings}")
    print(f"   Anomaly Ratio: {anomaly_ratio*100:.1f}%")
    print(f"   Expected Anomalies: {int(num_readings * anomaly_ratio)}")

    # Generate test data
    generator = SyntheticDataGenerator(plot, num_readings)
    readings, ground_truth = generator.generate_test_dataset(anomaly_ratio)

    print(f"\n✅ Generated {len(readings)} sensor readings")
    print(f"   Ground truth anomalies: {sum(1 for v in ground_truth.values() if v[0])}")

    # Wait a moment for signals to process
    import time
    time.sleep(2)

    # Evaluate
    evaluator = AnomalyEvaluator()
    for reading_id, (is_anomaly, anomaly_type) in ground_truth.items():
        evaluator.add_ground_truth(reading_id, is_anomaly, anomaly_type)
    
    evaluator.load_predictions_from_readings(readings)

    metrics = evaluator.calculate_metrics()
    print_evaluation_report(metrics)

    return metrics


