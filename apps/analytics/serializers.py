from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    node_code = serializers.CharField(source='node.code', read_only=True, allow_null=True)
    train_number = serializers.CharField(source='train.train_number', read_only=True, allow_null=True)
    acknowledged_by_username = serializers.CharField(
        source='acknowledged_by.username', read_only=True, allow_null=True
    )

    class Meta:
        model = Alert
        fields = [
            'id', 'alert_type', 'severity', 'title', 'message',
            'node', 'node_code', 'train', 'train_number', 'incident',
            'metadata',
            'is_acknowledged', 'acknowledged_by', 'acknowledged_by_username',
            'acknowledged_at', 'acknowledgement_notes',
            'auto_dismiss_at', 'is_dismissed', 'dismissed_at',
            'created_at',
        ]
        read_only_fields = [
            'id', 'is_acknowledged', 'acknowledged_by', 'acknowledged_at',
            'is_dismissed', 'dismissed_at', 'created_at',
        ]


class AlertAcknowledgeSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, default='', allow_blank=True)
