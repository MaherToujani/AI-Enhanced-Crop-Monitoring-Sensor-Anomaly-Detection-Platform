from django.db.models.signals import post_save
from django.dispatch import receiver

from ml_module.models import AnomalyEvent
from .agent import generate_recommendation


@receiver(post_save, sender=AnomalyEvent)
def run_agent_on_new_anomaly(
    sender, instance: AnomalyEvent, created: bool, **kwargs
):
    """
    When a new AnomalyEvent is created, trigger the rule-based agent
    to generate a recommendation.
    """

    if not created:
        return

    # Only generate a recommendation if none exists yet for this anomaly
    if instance.recommendations.exists():
        return

    generate_recommendation(instance)



