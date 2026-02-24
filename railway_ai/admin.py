"""
Django admin configuration for railway_ai models.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import MLModel, PredictionResult


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_type', 'version', 'algorithm', 'is_active_badge', 'trained_at')
    list_filter = ('model_type', 'is_active', 'algorithm', 'trained_at')
    search_fields = ('name', 'version', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at', 'performance_summary')
    autocomplete_fields = ['trained_by']
    date_hierarchy = 'trained_at'
    fieldsets = (
        ('Model Information', {
            'fields': ('name', 'model_type', 'version', 'algorithm', 'description')
        }),
        ('Artifacts & Status', {
            'fields': ('model_path', 'is_active')
        }),
        ('Performance', {
            'fields': ('metrics', 'performance_summary')
        }),
        ('Training Info', {
            'fields': (
                'trained_at',
                'trained_by',
                'training_duration_seconds',
                'training_data_size',
                'training_date_range_start',
                'training_date_range_end'
            ),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': ('hyperparameters',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 10px; border-radius: 3px;">Active</span>'
            )
        return format_html(
            '<span style="background-color: gray; color: white; padding: 3px 10px; border-radius: 3px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'

    def performance_summary(self, obj):
        return obj.get_performance_summary()
    performance_summary.short_description = 'Performance Metrics'

    actions = ['activate_model']

    def activate_model(self, request, queryset):
        for model in queryset:
            model.activate()
        self.message_user(request, f"{queryset.count()} model(s) activated.")
    activate_model.short_description = "Activate selected models"


@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    list_display = (
        'model_type_display',
        'target_display',
        'target_time',
        'confidence_score',
        'has_feedback',
        'prediction_time'
    )
    list_filter = ('model__model_type', 'node', 'prediction_time')
    search_fields = ('node__code', 'train__train_number')
    readonly_fields = ('id', 'created_at', 'updated_at', 'risk_level_display')
    autocomplete_fields = ['model', 'node', 'train']
    date_hierarchy = 'prediction_time'
    fieldsets = (
        ('Prediction Details', {
            'fields': ('model', 'prediction_time', 'target_time')
        }),
        ('Target', {
            'fields': ('node', 'train')
        }),
        ('Results', {
            'fields': ('prediction_value', 'confidence_score', 'risk_level_display')
        }),
        ('Feedback Loop', {
            'fields': ('actual_outcome', 'accuracy', 'feedback_recorded_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def model_type_display(self, obj):
        return obj.model.get_model_type_display()
    model_type_display.short_description = 'Model Type'

    def target_display(self, obj):
        if obj.node:
            return obj.node.code
        elif obj.train:
            return obj.train.train_number
        return 'General'
    target_display.short_description = 'Target'

    def has_feedback(self, obj):
        if obj.actual_outcome:
            return format_html(
                '<span style="color: green;">✓</span>'
            )
        return format_html(
            '<span style="color: gray;">✗</span>'
        )
    has_feedback.short_description = 'Feedback'

    def risk_level_display(self, obj):
        risk_level = obj.get_risk_level()
        if not risk_level:
            return 'N/A'

        colors = {
            'LOW': 'green',
            'MEDIUM': 'orange',
            'HIGH': 'red',
            'CRITICAL': 'darkred'
        }
        color = colors.get(risk_level, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            risk_level
        )
    risk_level_display.short_description = 'Risk Level'
