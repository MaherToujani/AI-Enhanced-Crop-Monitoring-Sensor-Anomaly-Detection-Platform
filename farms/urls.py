from rest_framework.routers import DefaultRouter

from .views import FarmProfileViewSet, FieldPlotViewSet

router = DefaultRouter()
router.register(r"farms", FarmProfileViewSet, basename="farm")
router.register(r"plots", FieldPlotViewSet, basename="plot")

urlpatterns = router.urls



