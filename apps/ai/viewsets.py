from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.api_permissions import IsAdminUser, CanViewReports

from .models import MLModel, PredictionResult
from .serializers import MLModelSerializer, PredictionResultSerializer


class MLModelViewSet(viewsets.ModelViewSet):
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['model_type', 'is_active', 'algorithm']
    search_fields = ['name', 'version', 'algorithm', 'description']
    ordering_fields = ['trained_at', 'version', 'model_type']

    @action(detail=True, methods=['post'], url_path='activate')
    def activate(self, request, pk=None):
        model = self.get_object()
        model.activate()
        return Response(MLModelSerializer(model).data)


class PredictionResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PredictionResult.objects.select_related('model', 'node', 'train').all()
    serializer_class = PredictionResultSerializer
    permission_classes = [CanViewReports]
    filterset_fields = ['model', 'node', 'train']
    search_fields = ['node__code', 'train__train_number']
    ordering_fields = ['prediction_time', 'target_time', 'confidence_score']
