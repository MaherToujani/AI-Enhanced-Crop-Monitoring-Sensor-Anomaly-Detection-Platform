from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ml_module.models import AnomalyEvent
from .models import AgentRecommendation


"""
Rule-based agent for generating recommendations and explanations.
Rules are deterministic, based on anomaly_type and severity.
"""


@dataclass
class AgentDecision:
    recommended_action: str
    explanation_text: str
    confidence: str  # "low" | "medium" | "high"


class RuleBasedAgent:
    def decide(self, anomaly: AnomalyEvent) -> Optional[AgentDecision]:
        """Generate recommendation based on anomaly type."""

        if anomaly.anomaly_type == AnomalyEvent.ANOMALY_IRRIGATION:
            return self._for_irrigation_issue(anomaly)

        if anomaly.anomaly_type == AnomalyEvent.ANOMALY_HEAT_STRESS:
            return self._for_heat_stress(anomaly)

        if anomaly.anomaly_type == AnomalyEvent.ANOMALY_COLD_STRESS:
            return self._for_cold_stress(anomaly)

        if anomaly.anomaly_type == AnomalyEvent.ANOMALY_SENSOR:
            return self._for_sensor_issue(anomaly)

        return self._for_general_anomaly(anomaly)

    def _for_irrigation_issue(self, anomaly: AnomalyEvent) -> AgentDecision:
        details = anomaly.details or {}
        value = details.get("value")
        threshold = details.get("threshold", 35)

        if anomaly.severity == AnomalyEvent.SEVERITY_HIGH:
            action = "Immediately inspect and repair the irrigation system for this plot."
            confidence = AgentRecommendation.CONFIDENCE_HIGH
        else:
            action = "Schedule an irrigation system check and increase watering frequency."
            confidence = AgentRecommendation.CONFIDENCE_MEDIUM

        explanation = (
            f"On {anomaly.timestamp:%Y-%m-%d %H:%M}, soil moisture on plot "
            f"'{anomaly.plot.name}' dropped below {threshold}% "
            f"(measured value: {value}%). This indicates a potential irrigation issue. "
            f"{action}"
        )

        return AgentDecision(
            recommended_action=action,
            explanation_text=explanation,
            confidence=confidence,
        )

    def _for_heat_stress(self, anomaly: AnomalyEvent) -> AgentDecision:
        details = anomaly.details or {}
        value = details.get("value")

        action = "Increase irrigation frequency and provide shade if possible."
        confidence = (
            AgentRecommendation.CONFIDENCE_HIGH
            if anomaly.severity == AnomalyEvent.SEVERITY_HIGH
            else AgentRecommendation.CONFIDENCE_MEDIUM
        )

        explanation = (
            f"On {anomaly.timestamp:%Y-%m-%d %H:%M}, air temperature on plot "
            f"'{anomaly.plot.name}' exceeded the safe range (measured: {value}°C). "
            f"This suggests heat stress on crops. {action}"
        )

        return AgentDecision(
            recommended_action=action,
            explanation_text=explanation,
            confidence=confidence,
        )

    def _for_cold_stress(self, anomaly: AnomalyEvent) -> AgentDecision:
        details = anomaly.details or {}
        value = details.get("value")

        action = "Prepare frost protection measures and monitor temperature closely."
        confidence = AgentRecommendation.CONFIDENCE_MEDIUM

        explanation = (
            f"On {anomaly.timestamp:%Y-%m-%d %H:%M}, air temperature on plot "
            f"'{anomaly.plot.name}' dropped below the safe range (measured: {value}°C). "
            f"This may cause cold stress. {action}"
        )

        return AgentDecision(
            recommended_action=action,
            explanation_text=explanation,
            confidence=confidence,
        )

    def _for_sensor_issue(self, anomaly: AnomalyEvent) -> AgentDecision:
        action = "Inspect the sensor hardware and wiring; recalibrate or replace if needed."
        confidence = AgentRecommendation.CONFIDENCE_MEDIUM

        explanation = (
            f"An anomaly of type 'sensor malfunction' was detected on plot "
            f"'{anomaly.plot.name}'. Readings are inconsistent with expected patterns. "
            f"{action}"
        )

        return AgentDecision(
            recommended_action=action,
            explanation_text=explanation,
            confidence=confidence,
        )

    def _for_general_anomaly(self, anomaly: AnomalyEvent) -> AgentDecision:
        action = "Perform a field inspection to identify possible stress factors."
        confidence = AgentRecommendation.CONFIDENCE_LOW

        explanation = (
            f"An environmental anomaly was detected on plot '{anomaly.plot.name}' "
            f"at {anomaly.timestamp:%Y-%m-%d %H:%M}. Sensor values deviated from "
            f"normal ranges. {action}"
        )

        return AgentDecision(
            recommended_action=action,
            explanation_text=explanation,
            confidence=confidence,
        )


def generate_recommendation(anomaly: AnomalyEvent) -> Optional[AgentRecommendation]:
    """
    High-level helper:
    - Run rule-based agent on an anomaly
    - If a decision is produced, create and return AgentRecommendation
    """

    agent = RuleBasedAgent()
    decision = agent.decide(anomaly)
    if decision is None:
        return None

    return AgentRecommendation.objects.create(
        anomaly_event=anomaly,
        recommended_action=decision.recommended_action,
        explanation_text=decision.explanation_text,
        confidence=decision.confidence,
    )



