from rest_framework import serializers
from .models import MLModel, PredictionResult


class MLModelSerializer(serializers.ModelSerializer):
    model_type_display = serializers.CharField(source='get_model_type_display', read_only=True)
    performance_summary = serializers.SerializerMethodField()

    class Meta:
        model = MLModel
        fields = [
            'id', 'name', 'model_type', 'model_type_display', 'version',
            'algorithm', 'model_path', 'metrics', 'trained_at', 'trained_by',
            'training_duration_seconds', 'training_data_size',
            'training_date_range_start', 'training_date_range_end',
            'hyperparameters', 'is_active', 'description',
            'performance_summary',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_performance_summary(self, obj):
        return obj.get_performance_summary()


class PredictionResultSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='model.name', read_only=True)
    model_type = serializers.CharField(source='model.model_type', read_only=True)
    node_code = serializers.CharField(source='node.code', read_only=True, allow_null=True)
    train_number = serializers.CharField(source='train.train_number', read_only=True, allow_null=True)
    risk_level = serializers.SerializerMethodField()

    class Meta:
        model = PredictionResult
        fields = [
            'id', 'model', 'model_name', 'model_type',
            'prediction_time', 'target_time',
            'node', 'node_code', 'train', 'train_number',
            'prediction_value', 'confidence_score',
            'actual_outcome', 'accuracy', 'feedback_recorded_at',
            'risk_level', 'metadata',
            'created_at',
        ]
        read_only_fields = fields

    def get_risk_level(self, obj):
        return obj.get_risk_level()
