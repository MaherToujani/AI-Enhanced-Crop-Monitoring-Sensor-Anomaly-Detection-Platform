"""
Evaluation Metrics Module for Anomaly Detection

This module provides functions to calculate precision, recall, F1-score,
and false positive rate for the ML anomaly detection model.
"""

from typing import List, Tuple, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta

from ml_module.models import AnomalyEvent
from sensors.models import SensorReading


@dataclass
class EvaluationMetrics:
    """Container for evaluation metrics."""
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    total_predictions: int
    total_actual_anomalies: int
    total_normal_readings: int


class AnomalyEvaluator:
    """Evaluates ML model performance using ground truth labels."""

    def __init__(self):
        self.predictions: List[Tuple[int, bool, str]] = []
        self.ground_truth: Dict[int, Tuple[bool, str]] = {}

    def add_ground_truth(self, reading_id: int, is_anomaly: bool, anomaly_type: str = None):
        """Add ground truth label for a sensor reading."""
        self.ground_truth[reading_id] = (is_anomaly, anomaly_type)

    def load_predictions_from_anomaly_events(self, anomaly_events: List[AnomalyEvent]):
        """Load predictions from AnomalyEvent records."""
        for event in anomaly_events:
            if event.sensor_reading:
                reading_id = event.sensor_reading.id
                self.predictions.append((reading_id, True, event.anomaly_type))

    def load_predictions_from_readings(self, readings: List[SensorReading]):
        """Load predictions by checking which readings have associated anomalies."""
        anomaly_reading_ids = set(
            AnomalyEvent.objects.filter(
                sensor_reading__in=readings
            ).values_list('sensor_reading_id', flat=True)
        )
        
        for reading in readings:
            is_anomaly = reading.id in anomaly_reading_ids
            anomaly_type = None
            if is_anomaly:
                try:
                    event = AnomalyEvent.objects.get(sensor_reading=reading)
                    anomaly_type = event.anomaly_type
                except AnomalyEvent.DoesNotExist:
                    pass
            
            self.predictions.append((reading.id, is_anomaly, anomaly_type))

    def calculate_metrics(self) -> EvaluationMetrics:
        """Calculate precision, recall, F1-score, and false positive rate."""
        tp = 0
        fp = 0
        fn = 0
        tn = 0

        predicted_anomaly_ids = {pred[0] for pred in self.predictions if pred[1]}
        for reading_id, predicted_anomaly, _ in self.predictions:
            if reading_id not in self.ground_truth:
                continue
            
            actual_anomaly, _ = self.ground_truth[reading_id]
            
            if predicted_anomaly and actual_anomaly:
                tp += 1
            elif predicted_anomaly and not actual_anomaly:
                fp += 1
            elif not predicted_anomaly and actual_anomaly:
                fn += 1
            else:
                tn += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0

        total_predictions = tp + fp + fn + tn
        total_actual_anomalies = tp + fn
        total_normal_readings = fp + tn

        return EvaluationMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            false_positive_rate=false_positive_rate,
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
            true_negatives=tn,
            total_predictions=total_predictions,
            total_actual_anomalies=total_actual_anomalies,
            total_normal_readings=total_normal_readings,
        )

    def reset(self):
        """Reset predictions and ground truth."""
        self.predictions = []
        self.ground_truth = {}


def evaluate_model_performance(
    readings: List[SensorReading],
    ground_truth: Dict[int, Tuple[bool, str]]
) -> EvaluationMetrics:
    """
    Convenience function to evaluate model performance.
    
    Args:
        readings: List of SensorReading objects to evaluate
        ground_truth: Dictionary mapping reading_id to (is_anomaly, anomaly_type)
    
    Returns:
        EvaluationMetrics object
    """
    evaluator = AnomalyEvaluator()
    
    # Add ground truth
    for reading_id, (is_anomaly, anomaly_type) in ground_truth.items():
        evaluator.add_ground_truth(reading_id, is_anomaly, anomaly_type)
    
    # Load predictions
    evaluator.load_predictions_from_readings(readings)
    
    # Calculate and return metrics
    return evaluator.calculate_metrics()


def print_evaluation_report(metrics: EvaluationMetrics):
    """Print a formatted evaluation report."""
    print("\n" + "="*60)
    print("ANOMALY DETECTION MODEL EVALUATION REPORT")
    print("="*60)
    print(f"\n📊 Performance Metrics:")
    print(f"   Precision:        {metrics.precision:.4f} ({metrics.precision*100:.2f}%)")
    print(f"   Recall:           {metrics.recall:.4f} ({metrics.recall*100:.2f}%)")
    print(f"   F1-Score:         {metrics.f1_score:.4f} ({metrics.f1_score*100:.2f}%)")
    print(f"   False Pos. Rate:  {metrics.false_positive_rate:.4f} ({metrics.false_positive_rate*100:.2f}%)")
    
    print(f"\n📈 Confusion Matrix:")
    print(f"   True Positives:   {metrics.true_positives}")
    print(f"   False Positives:  {metrics.false_positives}")
    print(f"   False Negatives:  {metrics.false_negatives}")
    print(f"   True Negatives:   {metrics.true_negatives}")
    
    print(f"\n📋 Summary:")
    print(f"   Total Predictions:     {metrics.total_predictions}")
    print(f"   Actual Anomalies:     {metrics.total_actual_anomalies}")
    print(f"   Actual Normal:        {metrics.total_normal_readings}")
    print("="*60 + "\n")


