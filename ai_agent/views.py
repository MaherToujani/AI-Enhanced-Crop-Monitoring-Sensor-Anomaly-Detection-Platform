from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter

from .models import AgentRecommendation
from .serializers import AgentRecommendationSerializer


class AgentRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API endpoint for viewing agent recommendations.
    Recommendations will be created automatically in a later phase.
    """

    serializer_class = AgentRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ["timestamp", "confidence"]
    ordering = ["-timestamp"]

    def get_queryset(self):
        user = self.request.user
        qs = AgentRecommendation.objects.select_related(
            "anomaly_event", "anomaly_event__plot", "anomaly_event__plot__farm"
        )
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return qs
        return qs.filter(anomaly_event__plot__farm__owner=user)
