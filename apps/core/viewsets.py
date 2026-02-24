from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q

from apps.common.api_mixins import SoftDeleteQuerySetMixin, SoftDeleteDestroyMixin
from apps.common.api_permissions import CanManageNodes, CanManageSchedules, CanManageIncidents

from .models import Node, Track, Train, Schedule, Event, Incident
from .serializers import (
    NodeSerializer, NodeListSerializer, TrackSerializer,
    TrainSerializer, ScheduleSerializer, EventSerializer,
    IncidentSerializer, IncidentResolveSerializer,
)


class NodeViewSet(SoftDeleteQuerySetMixin, SoftDeleteDestroyMixin, viewsets.ModelViewSet):
    queryset = Node.objects.all()
    permission_classes = [CanManageNodes]
    filterset_fields = ['node_type']
    search_fields = ['code', 'name']
    ordering_fields = ['name', 'code', 'created_at', 'capacity']

    def get_serializer_class(self):
        if self.action == 'list':
            return NodeListSerializer
        return NodeSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            qs = qs.annotate(track_count=Count('tracks', filter=Q(tracks__is_deleted=False)))
        return qs


class TrackViewSet(SoftDeleteQuerySetMixin, SoftDeleteDestroyMixin, viewsets.ModelViewSet):
    queryset = Track.objects.select_related('node').all()
    serializer_class = TrackSerializer
    permission_classes = [CanManageNodes]
    filterset_fields = ['node', 'direction', 'status']
    search_fields = ['code', 'name', 'node__code']
    ordering_fields = ['code', 'track_number', 'max_speed_kmh']


class TrainViewSet(SoftDeleteQuerySetMixin, SoftDeleteDestroyMixin, viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer
    permission_classes = [CanManageNodes]
    filterset_fields = ['train_type', 'operator']
    search_fields = ['train_number', 'operator']
    ordering_fields = ['train_number', 'train_type', 'max_speed_kmh']


class ScheduleViewSet(SoftDeleteQuerySetMixin, SoftDeleteDestroyMixin, viewsets.ModelViewSet):
    queryset = Schedule.objects.select_related('train', 'node', 'track').all()
    serializer_class = ScheduleSerializer
    permission_classes = [CanManageSchedules]
    filterset_fields = ['train', 'node', 'status', 'track']
    search_fields = ['train__train_number', 'node__code']
    ordering_fields = ['scheduled_arrival', 'scheduled_departure', 'delay_minutes', 'status']


class EventViewSet(SoftDeleteQuerySetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.select_related('train', 'node', 'track').all()
    serializer_class = EventSerializer
    filterset_fields = ['event_type', 'severity', 'train', 'node']
    search_fields = ['description', 'node__code', 'train__train_number']
    ordering_fields = ['timestamp', 'severity', 'event_type']


class IncidentViewSet(SoftDeleteQuerySetMixin, SoftDeleteDestroyMixin, viewsets.ModelViewSet):
    queryset = Incident.objects.select_related('node', 'reported_by').all()
    serializer_class = IncidentSerializer
    permission_classes = [CanManageIncidents]
    filterset_fields = ['incident_type', 'severity', 'status', 'node']
    search_fields = ['title', 'description', 'node__code']
    ordering_fields = ['started_at', 'severity', 'status']

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve_incident(self, request, pk=None):
        incident = self.get_object()
        ser = IncidentResolveSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        incident.resolve(resolution_notes=ser.validated_data['resolution_notes'])
        return Response(IncidentSerializer(incident).data)
