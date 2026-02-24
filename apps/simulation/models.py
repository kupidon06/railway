"""
Simulation engine models for scenario testing.

Contains models for creating and running railway operation simulations.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.common.models import TimeStampedModel, SoftDeleteModel
from apps.core.models import Node


class SimulationScenario(TimeStampedModel, SoftDeleteModel):
    """
    Predefined simulation scenario.

    Defines a specific scenario to test (e.g., train delay, track closure).
    """

    class ScenarioType(models.TextChoices):
        DELAY = 'DELAY', 'Train Delay'
        CLOSURE = 'CLOSURE', 'Track Closure'
        CONGESTION = 'CONGESTION', 'Congestion'
        INCIDENT = 'INCIDENT', 'Incident Response'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance Window'
        CUSTOM = 'CUSTOM', 'Custom Scenario'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Scenario name")
    description = models.TextField(help_text="Detailed scenario description")
    scenario_type = models.CharField(max_length=50, choices=ScenarioType.choices)

    # Scenario parameters stored as JSON
    # Example for DELAY: {"train_id": "uuid", "delay_minutes": 30, "start_time": "2024-03-20T10:00:00Z"}
    # Example for CLOSURE: {"track_ids": ["uuid1", "uuid2"], "start_time": "...", "duration_minutes": 120}
    parameters = models.JSONField(
        default=dict,
        help_text="Scenario configuration parameters (JSON)"
    )

    # Target node/network
    target_node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='simulation_scenarios',
        null=True,
        blank=True,
        help_text="Primary node affected by scenario"
    )

    # Creator
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_scenarios'
    )

    # Scenario metadata
    is_template = models.BooleanField(
        default=False,
        help_text="Is this a template scenario?"
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for categorization"
    )

    class Meta:
        indexes = [
            models.Index(fields=['scenario_type']),
            models.Index(fields=['target_node']),
            models.Index(fields=['is_template']),
            models.Index(fields=['is_deleted']),
        ]
        ordering = ['-created_at']
        verbose_name = 'Simulation Scenario'
        verbose_name_plural = 'Simulation Scenarios'

    def __str__(self):
        return f"{self.name} ({self.get_scenario_type_display()})"

    def clone(self, name=None, created_by=None):
        """Create a copy of this scenario."""
        clone = SimulationScenario.objects.create(
            name=name or f"{self.name} (Copy)",
            description=self.description,
            scenario_type=self.scenario_type,
            parameters=self.parameters.copy(),
            target_node=self.target_node,
            created_by=created_by or self.created_by,
            is_template=False,
            tags=self.tags.copy() if self.tags else []
        )
        return clone


class SimulationRun(TimeStampedModel):
    """
    Execution instance of a simulation scenario.

    Tracks the running and results of a specific simulation.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        RUNNING = 'RUNNING', 'Running'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scenario = models.ForeignKey(
        SimulationScenario,
        on_delete=models.CASCADE,
        related_name='runs'
    )

    # Execution tracking
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    # Simulation results stored as JSON
    # Example: {
    #   "affected_trains": 15,
    #   "total_delay_minutes": 450,
    #   "conflicts_detected": 3,
    #   "alternative_routes": [...],
    #   "timeline": [...],
    #   "kpis": {...}
    # }
    results = models.JSONField(
        default=dict,
        blank=True,
        help_text="Simulation results and analysis (JSON)"
    )

    # Error tracking
    error_message = models.TextField(
        blank=True,
        help_text="Error details if simulation failed"
    )

    # Execution metadata
    run_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='simulation_runs'
    )
    execution_time_seconds = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total execution time"
    )

    # Notes and annotations
    notes = models.TextField(
        blank=True,
        help_text="User notes about this simulation run"
    )

    class Meta:
        indexes = [
            models.Index(fields=['scenario', 'started_at']),
            models.Index(fields=['status']),
            models.Index(fields=['run_by']),
            models.Index(fields=['started_at']),
        ]
        ordering = ['-started_at']
        verbose_name = 'Simulation Run'
        verbose_name_plural = 'Simulation Runs'

    def __str__(self):
        return f"{self.scenario.name} - {self.started_at.strftime('%Y-%m-%d %H:%M')} ({self.status})"

    def mark_completed(self, results=None):
        """Mark simulation as completed."""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        if results:
            self.results = results
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.execution_time_seconds = delta.total_seconds()
        self.save(update_fields=['status', 'completed_at', 'results', 'execution_time_seconds'])

    def mark_failed(self, error_message=''):
        """Mark simulation as failed."""
        self.status = self.Status.FAILED
        self.completed_at = timezone.now()
        self.error_message = error_message
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.execution_time_seconds = delta.total_seconds()
        self.save(update_fields=['status', 'completed_at', 'error_message', 'execution_time_seconds'])

    def get_summary(self):
        """Get a summary of simulation results."""
        if not self.results:
            return {}
        return {
            'affected_trains': self.results.get('affected_trains', 0),
            'total_delay': self.results.get('total_delay_minutes', 0),
            'conflicts': self.results.get('conflicts_detected', 0),
            'duration': self.execution_time_seconds,
            'status': self.status
        }
