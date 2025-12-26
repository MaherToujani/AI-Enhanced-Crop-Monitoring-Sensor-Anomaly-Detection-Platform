from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import SensorReading
from .serializers import SensorReadingSerializer


class SensorReadingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for creating and viewing sensor readings.

    This will later be used by the simulator (for POST) and the frontend (for GET).
    """

    serializer_class = SensorReadingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ["timestamp", "sensor_type", "plot"]
    search_fields = ["plot__name", "plot__farm__name"]

    def get_queryset(self):
        user = self.request.user
        qs = SensorReading.objects.select_related("plot", "plot__farm")
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return qs
        return qs.filter(plot__farm__owner=user)

    def perform_create(self, serializer):
        # For now, any authenticated user can post readings to their own plots.
        # In the simulator phase we will post with a farm user or service user.
        serializer.save()
