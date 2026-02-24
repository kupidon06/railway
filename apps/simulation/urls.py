from rest_framework.routers import DefaultRouter
from .viewsets import SimulationScenarioViewSet, SimulationRunViewSet

router = DefaultRouter()
router.register(r'scenarios', SimulationScenarioViewSet, basename='scenario')
router.register(r'runs', SimulationRunViewSet, basename='run')

urlpatterns = router.urls
