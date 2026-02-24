from rest_framework.routers import DefaultRouter
from .viewsets import MLModelViewSet, PredictionResultViewSet

router = DefaultRouter()
router.register(r'models', MLModelViewSet, basename='mlmodel')
router.register(r'predictions', PredictionResultViewSet, basename='prediction')

urlpatterns = router.urls
