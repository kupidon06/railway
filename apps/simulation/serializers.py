from rest_framework import serializers
from .models import SimulationScenario, SimulationRun


class SimulationScenarioSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    run_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SimulationScenario
        fields = [
            'id', 'name', 'description', 'scenario_type', 'parameters',
            'target_node', 'created_by', 'created_by_username',
            'is_template', 'tags', 'run_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class SimulationRunSerializer(serializers.ModelSerializer):
    scenario_name = serializers.CharField(source='scenario.name', read_only=True)
    run_by_username = serializers.CharField(source='run_by.username', read_only=True, allow_null=True)
    summary = serializers.SerializerMethodField()

    class Meta:
        model = SimulationRun
        fields = [
            'id', 'scenario', 'scenario_name',
            'started_at', 'completed_at', 'status',
            'results', 'error_message',
            'run_by', 'run_by_username', 'execution_time_seconds',
            'notes', 'summary',
            'created_at',
        ]
        read_only_fields = [
            'id', 'run_by', 'started_at', 'completed_at',
            'results', 'error_message', 'execution_time_seconds', 'created_at',
        ]

    def get_summary(self, obj):
        return obj.get_summary()


class SimulationRunCreateSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, default='', allow_blank=True)
