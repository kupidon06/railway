from rest_framework.routers import DefaultRouter
from .viewsets import TrainPositionViewSet

router = DefaultRouter()
router.register(r'positions', TrainPositionViewSet, basename='trainposition')

urlpatterns = router.urls
