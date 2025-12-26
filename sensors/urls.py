from rest_framework.routers import DefaultRouter

from .views import SensorReadingViewSet

router = DefaultRouter()
router.register(r"sensor-readings", SensorReadingViewSet, basename="sensor-reading")

urlpatterns = router.urls



