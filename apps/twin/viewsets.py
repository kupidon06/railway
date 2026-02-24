from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Max

from .models import TrainPosition
from .serializers import TrainPositionSerializer


class TrainPositionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TrainPosition.objects.select_related('train', 'current_node', 'current_track').all()
    serializer_class = TrainPositionSerializer
    filterset_fields = ['train', 'current_node', 'status']
    search_fields = ['train__train_number', 'current_node__code']
    ordering_fields = ['timestamp', 'speed_kmh']

    @action(detail=False, methods=['get'], url_path='latest')
    def latest(self, request):
        """Get latest position for each train."""
        latest_ids = (
            TrainPosition.objects
            .values('train')
            .annotate(latest_id=Max('id'))
            .values_list('latest_id', flat=True)
        )
        qs = TrainPosition.objects.filter(
            id__in=latest_ids
        ).select_related('train', 'current_node', 'current_track')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
