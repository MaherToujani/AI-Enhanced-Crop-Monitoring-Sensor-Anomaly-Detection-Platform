from rest_framework.routers import DefaultRouter

from .views import AgentRecommendationViewSet

router = DefaultRouter()
router.register(
    r"recommendations", AgentRecommendationViewSet, basename="recommendation"
)

urlpatterns = router.urls



