from rest_framework.routers import DefaultRouter
from .viewsets import (
    NodeViewSet, TrackViewSet, TrainViewSet,
    ScheduleViewSet, EventViewSet, IncidentViewSet,
)

router = DefaultRouter()
router.register(r'nodes', NodeViewSet, basename='node')
router.register(r'tracks', TrackViewSet, basename='track')
router.register(r'trains', TrainViewSet, basename='train')
router.register(r'schedules', ScheduleViewSet, basename='schedule')
router.register(r'events', EventViewSet, basename='event')
router.register(r'incidents', IncidentViewSet, basename='incident')

urlpatterns = router.urls
