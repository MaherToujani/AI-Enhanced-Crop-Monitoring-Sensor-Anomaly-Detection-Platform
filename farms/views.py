from rest_framework import permissions, viewsets

from .models import FarmProfile, FieldPlot
from .serializers import FarmProfileSerializer, FieldPlotSerializer


class FarmProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for listing and managing farms.

    For now, we keep permissions simple: authenticated users only.
    In Phase 3 we will refine this to enforce farmer/admin roles.
    """

    serializer_class = FarmProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return FarmProfile.objects.all()
        return FarmProfile.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class FieldPlotViewSet(viewsets.ModelViewSet):
    """
    API endpoint for listing and managing plots.
    """

    serializer_class = FieldPlotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = FieldPlot.objects.select_related("farm", "farm__owner")
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return qs
        return qs.filter(farm__owner=user)
