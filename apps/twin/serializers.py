from rest_framework import serializers
from .models import TrainPosition


class TrainPositionSerializer(serializers.ModelSerializer):
    train_number = serializers.CharField(source='train.train_number', read_only=True)
    node_code = serializers.CharField(source='current_node.code', read_only=True, allow_null=True)

    class Meta:
        model = TrainPosition
        fields = [
            'id', 'timestamp', 'train', 'train_number',
            'current_node', 'node_code', 'current_track',
            'latitude', 'longitude', 'speed_kmh', 'status', 'metadata',
            'created_at',
        ]
        read_only_fields = fields
