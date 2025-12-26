from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter

from .models import AnomalyEvent
from .serializers import AnomalyEventSerializer


class AnomalyEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API endpoint for viewing anomalies.
    Creation is handled by the ML module, not directly via API.
    """

    serializer_class = AnomalyEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ["timestamp", "severity", "model_confidence"]
    ordering = ["-timestamp"]

    def get_queryset(self):
        user = self.request.user
        qs = AnomalyEvent.objects.select_related("plot", "plot__farm")
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return qs
        return qs.filter(plot__farm__owner=user)
