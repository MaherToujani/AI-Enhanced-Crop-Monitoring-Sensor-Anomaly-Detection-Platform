from rest_framework.routers import DefaultRouter

from .views import AnomalyEventViewSet

router = DefaultRouter()
router.register(r"anomalies", AnomalyEventViewSet, basename="anomaly")

urlpatterns = router.urls



