"""
AI/ML models for predictive analytics.

Contains models for ML model versioning and prediction storage.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import TimeStampedModel


class MLModel(TimeStampedModel):
    """
    Machine Learning model version and metadata.

    Tracks different versions of ML models used for predictions.
    """

    class ModelType(models.TextChoices):
        CONGESTION_PREDICTION = 'CONGESTION_PREDICTION', 'Congestion Prediction'
        ANOMALY_DETECTION = 'ANOMALY_DETECTION', 'Anomaly Detection'
        RISK_SCORING = 'RISK_SCORING', 'Risk Scoring'
        DELAY_PREDICTION = 'DELAY_PREDICTION', 'Delay Prediction'
        DEMAND_FORECASTING = 'DEMAND_FORECASTING', 'Demand Forecasting'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Model name")
    model_type = models.CharField(max_length=50, choices=ModelType.choices)
    version = models.CharField(max_length=50, help_text="Model version (e.g., v1.0, v2.1)")
    algorithm = models.CharField(
        max_length=100,
        help_text="Algorithm used (e.g., RandomForest, LSTM, IsolationForest)"
    )

    # Model artifacts
    model_path = models.CharField(
        max_length=500,
        help_text="Path to model file (local or S3)"
    )

    # Model performance metrics stored as JSON
    # Example: {"accuracy": 0.87, "precision": 0.85, "recall": 0.89, "f1": 0.87, "mse": 12.3}
    metrics = models.JSONField(
        default=dict,
        help_text="Model performance metrics (JSON)"
    )

    # Training metadata
    trained_at = models.DateTimeField(help_text="When the model was trained")
    trained_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trained_models'
    )
    training_duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Training duration in seconds"
    )

    # Training data info
    training_data_size = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of training samples"
    )
    training_date_range_start = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Start date of training data"
    )
    training_date_range_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text="End date of training data"
    )

    # Model configuration
    hyperparameters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Model hyperparameters (JSON)"
    )

    # Status
    is_active = models.BooleanField(
        default=False,
        help_text="Is this the currently active model for its type?"
    )

    # Documentation
    description = models.TextField(
        blank=True,
        help_text="Model description and notes"
    )

    class Meta:
        indexes = [
            models.Index(fields=['model_type', 'is_active']),
            models.Index(fields=['version']),
            models.Index(fields=['trained_at']),
        ]
        ordering = ['-trained_at']
        verbose_name = 'ML Model'
        verbose_name_plural = 'ML Models'
        unique_together = ('model_type', 'version')

    def __str__(self):
        return f"{self.get_model_type_display()} - {self.version} ({'Active' if self.is_active else 'Inactive'})"

    def activate(self):
        """Set this model as the active model for its type."""
        # Deactivate all other models of the same type
        MLModel.objects.filter(model_type=self.model_type, is_active=True).update(is_active=False)
        self.is_active = True
        self.save(update_fields=['is_active'])

    def get_performance_summary(self):
        """Get a summary of model performance."""
        if not self.metrics:
            return "No metrics available"

        key_metrics = []
        for metric in ['accuracy', 'precision', 'recall', 'f1', 'mse', 'rmse', 'mae']:
            if metric in self.metrics:
                key_metrics.append(f"{metric}: {self.metrics[metric]:.3f}")

        return ", ".join(key_metrics) if key_metrics else "No metrics available"


class PredictionResult(TimeStampedModel):
    """
    ML prediction output.

    Stores predictions made by ML models for analysis and feedback loops.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey(
        MLModel,
        on_delete=models.CASCADE,
        related_name='predictions'
    )

    # Prediction timing
    prediction_time = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="When the prediction was made"
    )
    target_time = models.DateTimeField(
        db_index=True,
        help_text="Time period being predicted"
    )

    # Target entities
    node = models.ForeignKey(
        'railway_core.Node',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='predictions'
    )
    train = models.ForeignKey(
        'railway_core.Train',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='predictions'
    )

    # Prediction outputs stored as JSON
    # Example for congestion: {"risk_score": 85, "probability": 0.73, "confidence": 0.89, "factors": [...]}
    # Example for anomaly: {"is_anomaly": true, "anomaly_score": 0.92, "detected_patterns": [...]}
    prediction_value = models.JSONField(
        help_text="Prediction output data (JSON)"
    )

    # Confidence score (0-1)
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Model confidence (0-1)"
    )

    # Feedback loop - actual outcome for model retraining
    actual_outcome = models.JSONField(
        null=True,
        blank=True,
        help_text="Actual outcome for comparison (JSON)"
    )
    accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Prediction accuracy (0-1)"
    )
    feedback_recorded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When feedback was recorded"
    )

    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional prediction metadata"
    )

    class Meta:
        indexes = [
            models.Index(fields=['prediction_time']),
            models.Index(fields=['target_time']),
            models.Index(fields=['node', 'target_time']),
            models.Index(fields=['train', 'target_time']),
            models.Index(fields=['model', 'prediction_time']),
        ]
        ordering = ['-prediction_time']
        verbose_name = 'Prediction Result'
        verbose_name_plural = 'Prediction Results'

    def __str__(self):
        target = self.node.code if self.node else (self.train.train_number if self.train else 'General')
        return f"{self.model.get_model_type_display()} for {target} at {self.target_time.strftime('%Y-%m-%d %H:%M')}"

    def record_feedback(self, actual_outcome):
        """Record actual outcome for model improvement."""
        self.actual_outcome = actual_outcome
        self.feedback_recorded_at = timezone.now()

        # Calculate accuracy if possible
        if self.model.model_type == MLModel.ModelType.CONGESTION_PREDICTION:
            predicted_risk = self.prediction_value.get('risk_score', 0)
            actual_risk = actual_outcome.get('actual_risk_score', 0)
            if actual_risk > 0:
                self.accuracy = 1 - abs(predicted_risk - actual_risk) / 100

        self.save(update_fields=['actual_outcome', 'feedback_recorded_at', 'accuracy'])

    def get_risk_level(self):
        """Get human-readable risk level from prediction."""
        if self.model.model_type != MLModel.ModelType.RISK_SCORING:
            return None

        risk_score = self.prediction_value.get('risk_score', 0)
        if risk_score >= 80:
            return 'CRITICAL'
        elif risk_score >= 60:
            return 'HIGH'
        elif risk_score >= 40:
            return 'MEDIUM'
        else:
            return 'LOW'
