"""
Core data models for Railway Digital Twin system.

Contains foundational models: Node, Track, Train, Schedule, Event, Incident.
"""
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.common.models import TimeStampedModel, SoftDeleteModel


class Node(TimeStampedModel, SoftDeleteModel):
    """
    Railway node (station, junction, or depot).

    Represents a physical location in the railway network where trains stop or pass through.
    """

    class NodeType(models.TextChoices):
        STATION = 'STATION', 'Station'
        JUNCTION = 'JUNCTION', 'Junction'
        DEPOT = 'DEPOT', 'Depot'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, help_text="Unique node code (e.g., PARIS_NORD)")
    name = models.CharField(max_length=255, help_text="Full name of the node")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="GPS latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="GPS longitude")
    capacity = models.IntegerField(default=10, validators=[MinValueValidator(1)], help_text="Number of tracks")
    node_type = models.CharField(max_length=20, choices=NodeType.choices, default=NodeType.STATION)
    timezone = models.CharField(max_length=64, default="UTC", help_text="Timezone for this node")

    class Meta:
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['node_type']),
            models.Index(fields=['is_deleted']),
        ]
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_active_tracks(self):
        """Get all operational tracks for this node."""
        return self.tracks.filter(is_deleted=False, status='OPERATIONAL')

    def get_current_occupancy_rate(self):
        """Calculate current occupancy rate (0-100%)."""
        total_tracks = self.tracks.filter(is_deleted=False).count()
        if total_tracks == 0:
            return 0
        occupied_tracks = self.tracks.filter(
            is_deleted=False,
            schedules__status__in=['ON_TIME', 'DELAYED'],
            schedules__scheduled_arrival__lte=timezone.now(),
            schedules__scheduled_departure__gte=timezone.now()
        ).distinct().count()
        return (occupied_tracks / total_tracks) * 100


class Track(TimeStampedModel, SoftDeleteModel):
    """
    Physical track within a node.

    Represents a specific track that trains can occupy.
    """

    class Direction(models.TextChoices):
        INBOUND = 'INBOUND', 'Inbound'
        OUTBOUND = 'OUTBOUND', 'Outbound'
        BIDIRECTIONAL = 'BIDIRECTIONAL', 'Bidirectional'

    class Status(models.TextChoices):
        OPERATIONAL = 'OPERATIONAL', 'Operational'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance'
        CLOSED = 'CLOSED', 'Closed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True, help_text="Unique track code (e.g., T1A)")
    name = models.CharField(max_length=255, help_text="Track name or description")
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='tracks')
    track_number = models.IntegerField(validators=[MinValueValidator(1)])
    length_meters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Track length in meters"
    )
    max_speed_kmh = models.IntegerField(
        default=120,
        validators=[MinValueValidator(1), MaxValueValidator(400)],
        help_text="Maximum speed in km/h"
    )
    direction = models.CharField(max_length=20, choices=Direction.choices, default=Direction.BIDIRECTIONAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPERATIONAL)

    class Meta:
        unique_together = ('node', 'track_number')
        indexes = [
            models.Index(fields=['node', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['code']),
            models.Index(fields=['is_deleted']),
        ]
        ordering = ['node', 'track_number']

    def __str__(self):
        return f"{self.node.code} - Track {self.track_number} ({self.code})"

    def is_available(self):
        """Check if track is currently available for use."""
        return self.status == self.Status.OPERATIONAL and not self.is_deleted


class Train(TimeStampedModel, SoftDeleteModel):
    """
    Train entity.

    Represents a physical train that operates on the railway network.
    """

    class TrainType(models.TextChoices):
        TGV = 'TGV', 'TGV (High-Speed)'
        INTERCITE = 'INTERCITE', 'Intercité'
        TER = 'TER', 'TER (Regional)'
        CARGO = 'CARGO', 'Cargo'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    train_number = models.CharField(max_length=20, unique=True, help_text="Unique train identifier")
    train_type = models.CharField(max_length=50, choices=TrainType.choices)
    operator = models.CharField(max_length=100, help_text="Operating company")
    capacity_passengers = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Passenger capacity (null for cargo)"
    )
    length_meters = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(1)],
        help_text="Train length in meters"
    )
    max_speed_kmh = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(400)],
        help_text="Maximum speed in km/h"
    )

    class Meta:
        indexes = [
            models.Index(fields=['train_number']),
            models.Index(fields=['train_type']),
            models.Index(fields=['operator']),
            models.Index(fields=['is_deleted']),
        ]
        ordering = ['train_number']

    def __str__(self):
        return f"{self.train_number} ({self.get_train_type_display()})"

    def get_current_schedule(self):
        """Get current active schedule for this train."""
        now = timezone.now()
        return self.schedules.filter(
            scheduled_arrival__lte=now,
            scheduled_departure__gte=now,
            status__in=['SCHEDULED', 'ON_TIME', 'DELAYED']
        ).first()


class Schedule(TimeStampedModel, SoftDeleteModel):
    """
    Scheduled train movement at a node.

    Tracks both scheduled and actual arrival/departure times.
    """

    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        ON_TIME = 'ON_TIME', 'On Time'
        DELAYED = 'DELAYED', 'Delayed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        COMPLETED = 'COMPLETED', 'Completed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='schedules')
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='schedules')
    track = models.ForeignKey(Track, on_delete=models.SET_NULL, null=True, blank=True, related_name='schedules')

    scheduled_arrival = models.DateTimeField(db_index=True)
    scheduled_departure = models.DateTimeField(db_index=True)
    actual_arrival = models.DateTimeField(null=True, blank=True)
    actual_departure = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    delay_minutes = models.IntegerField(default=0, help_text="Delay in minutes (negative for early)")

    notes = models.TextField(blank=True, help_text="Additional notes or comments")

    class Meta:
        indexes = [
            models.Index(fields=['scheduled_arrival']),
            models.Index(fields=['scheduled_departure']),
            models.Index(fields=['train', 'scheduled_arrival']),
            models.Index(fields=['node', 'scheduled_arrival']),
            models.Index(fields=['status']),
            models.Index(fields=['is_deleted']),
        ]
        ordering = ['scheduled_arrival']

    def __str__(self):
        return f"{self.train.train_number} at {self.node.code} - {self.scheduled_arrival.strftime('%Y-%m-%d %H:%M')}"

    def calculate_delay(self):
        """Calculate delay based on actual vs scheduled times."""
        if self.actual_arrival and self.scheduled_arrival:
            delta = self.actual_arrival - self.scheduled_arrival
            return int(delta.total_seconds() / 60)
        return 0

    def update_status(self):
        """Automatically update status based on current time and delays."""
        now = timezone.now()

        if self.actual_departure:
            self.status = self.Status.COMPLETED
        elif self.status == self.Status.CANCELLED:
            pass  # Keep cancelled status
        elif self.delay_minutes > 5:
            self.status = self.Status.DELAYED
        elif now > self.scheduled_departure:
            self.status = self.Status.COMPLETED
        elif now >= self.scheduled_arrival:
            self.status = self.Status.ON_TIME
        else:
            self.status = self.Status.SCHEDULED

        return self.status


class Event(TimeStampedModel):
    """
    Time-series event log.

    Records all significant events in the railway system.
    Will be converted to TimescaleDB hypertable in production.
    """

    class EventType(models.TextChoices):
        ARRIVAL = 'ARRIVAL', 'Train Arrival'
        DEPARTURE = 'DEPARTURE', 'Train Departure'
        DELAY = 'DELAY', 'Delay'
        TRACK_CHANGE = 'TRACK_CHANGE', 'Track Change'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance'
        ALERT = 'ALERT', 'Alert'
        INCIDENT = 'INCIDENT', 'Incident'

    class Severity(models.TextChoices):
        INFO = 'INFO', 'Info'
        WARNING = 'WARNING', 'Warning'
        CRITICAL = 'CRITICAL', 'Critical'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(db_index=True, default=timezone.now)
    event_type = models.CharField(max_length=50, choices=EventType.choices)
    train = models.ForeignKey(Train, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='events')
    track = models.ForeignKey(Track, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.INFO)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional event data")

    class Meta:
        indexes = [
            models.Index(fields=['timestamp', 'event_type']),
            models.Index(fields=['node', 'timestamp']),
            models.Index(fields=['train', 'timestamp']),
            models.Index(fields=['severity']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_event_type_display()} at {self.node.code} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class Incident(TimeStampedModel, SoftDeleteModel):
    """
    Operational incident.

    Tracks issues that affect railway operations.
    """

    class IncidentType(models.TextChoices):
        TECHNICAL = 'TECHNICAL', 'Technical Issue'
        WEATHER = 'WEATHER', 'Weather'
        ACCIDENT = 'ACCIDENT', 'Accident'
        SECURITY = 'SECURITY', 'Security'
        STRIKE = 'STRIKE', 'Strike'
        OTHER = 'OTHER', 'Other'

    class Severity(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        MONITORING = 'MONITORING', 'Monitoring'
        RESOLVED = 'RESOLVED', 'Resolved'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    incident_type = models.CharField(max_length=50, choices=IncidentType.choices)
    severity = models.CharField(max_length=20, choices=Severity.choices)
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='incidents')
    affected_tracks = models.ManyToManyField(Track, blank=True, related_name='incidents')
    affected_trains = models.ManyToManyField(Train, blank=True, related_name='incidents')

    started_at = models.DateTimeField(default=timezone.now)
    resolved_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reported_incidents'
    )

    resolution_notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['node', 'status']),
            models.Index(fields=['started_at']),
            models.Index(fields=['severity', 'status']),
            models.Index(fields=['is_deleted']),
        ]
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.title} ({self.get_severity_display()}) - {self.node.code}"

    def resolve(self, resolution_notes=''):
        """Mark incident as resolved."""
        self.status = self.Status.RESOLVED
        self.resolved_at = timezone.now()
        self.resolution_notes = resolution_notes
        self.save(update_fields=['status', 'resolved_at', 'resolution_notes'])

    def get_duration(self):
        """Get incident duration in minutes."""
        end_time = self.resolved_at or timezone.now()
        delta = end_time - self.started_at
        return int(delta.total_seconds() / 60)
