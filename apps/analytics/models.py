"""
Analytics and reporting models.

Contains models for alerts, reports, and KPIs.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.common.models import TimeStampedModel
from apps.core.models import Node, Train, Incident


class Alert(TimeStampedModel):
    """
    System alert for operational issues.

    Generated automatically or manually for important events.
    """

    class AlertType(models.TextChoices):
        CONGESTION = 'CONGESTION', 'Congestion Alert'
        DELAY = 'DELAY', 'Delay Alert'
        INCIDENT = 'INCIDENT', 'Incident Alert'
        ANOMALY = 'ANOMALY', 'Anomaly Detected'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance Required'
        PREDICTION = 'PREDICTION', 'Prediction Alert'
        SYSTEM = 'SYSTEM', 'System Alert'

    class Severity(models.TextChoices):
        INFO = 'INFO', 'Info'
        WARNING = 'WARNING', 'Warning'
        CRITICAL = 'CRITICAL', 'Critical'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_type = models.CharField(max_length=50, choices=AlertType.choices)
    severity = models.CharField(max_length=20, choices=Severity.choices)
    title = models.CharField(max_length=255, help_text="Alert title")
    message = models.TextField(help_text="Detailed alert message")

    # Related entities
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alerts'
    )
    train = models.ForeignKey(
        Train,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )
    incident = models.ForeignKey(
        Incident,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )

    # Alert metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional alert data (JSON)"
    )

    # Acknowledgement tracking
    is_acknowledged = models.BooleanField(default=False, db_index=True)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledgement_notes = models.TextField(blank=True)

    # Auto-dismissal
    auto_dismiss_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Automatically dismiss alert at this time"
    )
    is_dismissed = models.BooleanField(default=False, db_index=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['alert_type', 'severity']),
            models.Index(fields=['is_acknowledged']),
            models.Index(fields=['is_dismissed']),
            models.Index(fields=['node', 'created_at']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
        verbose_name = 'Alert'
        verbose_name_plural = 'Alerts'

    def __str__(self):
        return f"{self.get_severity_display()}: {self.title}"

    def acknowledge(self, user, notes=''):
        """Acknowledge this alert."""
        self.is_acknowledged = True
        self.acknowledged_by = user
        self.acknowledged_at = timezone.now()
        self.acknowledgement_notes = notes
        self.save(update_fields=['is_acknowledged', 'acknowledged_by', 'acknowledged_at', 'acknowledgement_notes'])

    def dismiss(self):
        """Dismiss this alert."""
        self.is_dismissed = True
        self.dismissed_at = timezone.now()
        self.save(update_fields=['is_dismissed', 'dismissed_at'])

    @classmethod
    def get_active_alerts(cls, node=None):
        """Get all active (unacknowledged, undismissed) alerts."""
        queryset = cls.objects.filter(is_acknowledged=False, is_dismissed=False)
        if node:
            queryset = queryset.filter(node=node)
        return queryset.order_by('-severity', '-created_at')

    @classmethod
    def create_congestion_alert(cls, node, risk_score, details=None):
        """Helper to create a congestion alert."""
        severity = cls.Severity.CRITICAL if risk_score >= 80 else (
            cls.Severity.WARNING if risk_score >= 60 else cls.Severity.INFO
        )

        return cls.objects.create(
            alert_type=cls.AlertType.CONGESTION,
            severity=severity,
            title=f"Congestion Alert: {node.name}",
            message=f"High congestion detected at {node.name}. Risk score: {risk_score}%",
            node=node,
            metadata={'risk_score': risk_score, 'details': details or {}}
        )

    @classmethod
    def create_delay_alert(cls, train, delay_minutes, node=None):
        """Helper to create a delay alert."""
        severity = cls.Severity.CRITICAL if delay_minutes >= 30 else (
            cls.Severity.WARNING if delay_minutes >= 15 else cls.Severity.INFO
        )

        return cls.objects.create(
            alert_type=cls.AlertType.DELAY,
            severity=severity,
            title=f"Train Delay: {train.train_number}",
            message=f"Train {train.train_number} is delayed by {delay_minutes} minutes.",
            train=train,
            node=node,
            metadata={'delay_minutes': delay_minutes}
        )
