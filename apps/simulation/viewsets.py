from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count

from apps.common.api_mixins import SoftDeleteQuerySetMixin, SoftDeleteDestroyMixin
from apps.common.api_permissions import CanRunSimulation

from .models import SimulationScenario, SimulationRun
from .serializers import (
    SimulationScenarioSerializer, SimulationRunSerializer,
    SimulationRunCreateSerializer,
)


class SimulationScenarioViewSet(SoftDeleteQuerySetMixin, SoftDeleteDestroyMixin, viewsets.ModelViewSet):
    queryset = SimulationScenario.objects.select_related('target_node', 'created_by').all()
    serializer_class = SimulationScenarioSerializer
    permission_classes = [CanRunSimulation]
    filterset_fields = ['scenario_type', 'is_template', 'target_node']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'scenario_type']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(run_count=Count('runs'))

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='clone')
    def clone(self, request, pk=None):
        scenario = self.get_object()
        cloned = scenario.clone(
            name=request.data.get('name'),
            created_by=request.user
        )
        return Response(
            SimulationScenarioSerializer(cloned).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], url_path='run')
    def run_simulation(self, request, pk=None):
        scenario = self.get_object()
        ser = SimulationRunCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        run = SimulationRun.objects.create(
            scenario=scenario,
            run_by=request.user,
            notes=ser.validated_data.get('notes', ''),
            status=SimulationRun.Status.PENDING,
        )
        return Response(
            SimulationRunSerializer(run).data,
            status=status.HTTP_201_CREATED
        )


class SimulationRunViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SimulationRun.objects.select_related('scenario', 'run_by').all()
    serializer_class = SimulationRunSerializer
    permission_classes = [CanRunSimulation]
    filterset_fields = ['scenario', 'status', 'run_by']
    ordering_fields = ['started_at', 'completed_at', 'status']

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        run = self.get_object()
        if run.status not in (SimulationRun.Status.PENDING, SimulationRun.Status.RUNNING):
            return Response(
                {'error': 'Can only cancel pending or running simulations'},
                status=status.HTTP_400_BAD_REQUEST
            )
        run.status = SimulationRun.Status.CANCELLED
        run.save(update_fields=['status'])
        return Response(SimulationRunSerializer(run).data)
