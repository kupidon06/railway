from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.api_permissions import CanAcknowledgeAlerts
from apps.core.models import Node

from .models import Alert
from .serializers import AlertSerializer, AlertAcknowledgeSerializer


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related('node', 'train', 'incident', 'acknowledged_by').all()
    serializer_class = AlertSerializer
    permission_classes = [CanAcknowledgeAlerts]
    filterset_fields = ['alert_type', 'severity', 'is_acknowledged', 'is_dismissed', 'node', 'train']
    search_fields = ['title', 'message', 'node__code']
    ordering_fields = ['created_at', 'severity', 'alert_type']

    @action(detail=True, methods=['post'], url_path='acknowledge')
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        ser = AlertAcknowledgeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        alert.acknowledge(user=request.user, notes=ser.validated_data.get('notes', ''))
        return Response(AlertSerializer(alert).data)

    @action(detail=True, methods=['post'], url_path='dismiss')
    def dismiss(self, request, pk=None):
        alert = self.get_object()
        alert.dismiss()
        return Response(AlertSerializer(alert).data)

    @action(detail=False, methods=['get'], url_path='active')
    def active_alerts(self, request):
        node_id = request.query_params.get('node')
        node = Node.objects.get(pk=node_id) if node_id else None
        qs = Alert.get_active_alerts(node=node)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
