"""
Digital Twin models for real-time railway visualization.

Contains models for tracking real-time train positions and track occupancy.
"""
import uuid
from django.db import models
from django.utils import timezone
from apps.common.models import TimeStampedModel
from apps.core.models import Train, Node, Track


class TrainPosition(TimeStampedModel):
    """
    Real-time train position tracking.

    Will be converted to TimescaleDB hypertable in production for efficient time-series storage.
    """

    class Status(models.TextChoices):
        MOVING = 'MOVING', 'Moving'
        STOPPED = 'STOPPED', 'Stopped'
        BOARDING = 'BOARDING', 'Boarding'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(db_index=True, default=timezone.now)
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='positions')
    current_node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='current_trains'
    )
    current_track = models.ForeignKey(
        Track,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_trains'
    )

    # GPS coordinates (optional, for advanced tracking)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Movement data
    speed_kmh = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Current speed in km/h"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.STOPPED)

    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional tracking data")

    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['train', 'timestamp']),
            models.Index(fields=['current_node', 'timestamp']),
            models.Index(fields=['status']),
        ]
        ordering = ['-timestamp']
        verbose_name = 'Train Position'
        verbose_name_plural = 'Train Positions'

    def __str__(self):
        location = self.current_node.code if self.current_node else 'Unknown'
        return f"{self.train.train_number} at {location} - {self.timestamp.strftime('%H:%M:%S')}"

    def get_latest_for_train(train_id):
        """Get the most recent position for a train."""
        return TrainPosition.objects.filter(train_id=train_id).order_by('-timestamp').first()

    @classmethod
    def get_active_trains_at_node(cls, node):
        """Get all trains currently at a specific node."""
        # Get latest position for each train at this node (within last 5 minutes)
        five_minutes_ago = timezone.now() - timezone.timedelta(minutes=5)
        return cls.objects.filter(
            current_node=node,
            timestamp__gte=five_minutes_ago,
            status__in=[cls.Status.STOPPED, cls.Status.BOARDING]
        ).order_by('train', '-timestamp').distinct('train')
