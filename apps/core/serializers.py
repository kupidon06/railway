from rest_framework import serializers
from .models import Node, Track, Train, Schedule, Event, Incident


class TrackMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['id', 'code', 'track_number', 'direction', 'status']


class NodeSerializer(serializers.ModelSerializer):
    tracks = TrackMinimalSerializer(many=True, read_only=True, source='get_active_tracks')
    occupancy_rate = serializers.SerializerMethodField()

    class Meta:
        model = Node
        fields = [
            'id', 'code', 'name', 'latitude', 'longitude', 'capacity',
            'node_type', 'timezone', 'tracks', 'occupancy_rate',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_occupancy_rate(self, obj):
        return obj.get_current_occupancy_rate()


class NodeListSerializer(serializers.ModelSerializer):
    track_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Node
        fields = ['id', 'code', 'name', 'node_type', 'capacity', 'track_count']


class TrackSerializer(serializers.ModelSerializer):
    node_code = serializers.CharField(source='node.code', read_only=True)

    class Meta:
        model = Track
        fields = [
            'id', 'code', 'name', 'node', 'node_code', 'track_number',
            'length_meters', 'max_speed_kmh', 'direction', 'status',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TrainSerializer(serializers.ModelSerializer):
    train_type_display = serializers.CharField(source='get_train_type_display', read_only=True)

    class Meta:
        model = Train
        fields = [
            'id', 'train_number', 'train_type', 'train_type_display',
            'operator', 'capacity_passengers', 'length_meters', 'max_speed_kmh',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ScheduleSerializer(serializers.ModelSerializer):
    train_number = serializers.CharField(source='train.train_number', read_only=True)
    node_code = serializers.CharField(source='node.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Schedule
        fields = [
            'id', 'train', 'train_number', 'node', 'node_code',
            'track',
            'scheduled_arrival', 'scheduled_departure',
            'actual_arrival', 'actual_departure',
            'status', 'status_display', 'delay_minutes', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EventSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    node_code = serializers.CharField(source='node.code', read_only=True)
    train_number = serializers.CharField(source='train.train_number', read_only=True, allow_null=True)

    class Meta:
        model = Event
        fields = [
            'id', 'timestamp', 'event_type', 'event_type_display',
            'train', 'train_number', 'node', 'node_code', 'track',
            'severity', 'description', 'metadata',
            'created_at',
        ]
        read_only_fields = fields


class IncidentSerializer(serializers.ModelSerializer):
    node_code = serializers.CharField(source='node.code', read_only=True)
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True, allow_null=True)
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = [
            'id', 'title', 'description', 'incident_type', 'severity',
            'node', 'node_code', 'affected_tracks', 'affected_trains',
            'started_at', 'resolved_at', 'status',
            'reported_by', 'reported_by_username', 'resolution_notes',
            'duration_minutes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'resolved_at']

    def get_duration_minutes(self, obj):
        return obj.get_duration()


class IncidentResolveSerializer(serializers.Serializer):
    resolution_notes = serializers.CharField(required=False, default='', allow_blank=True)
