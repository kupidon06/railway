"""
Django admin configuration for railway_simulation models.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import SimulationScenario, SimulationRun
from apps.core.models import Node


@admin.register(SimulationScenario)
class SimulationScenarioAdmin(admin.ModelAdmin):
    list_display = ('name', 'scenario_type', 'target_node', 'is_template', 'created_by', 'created_at')
    list_filter = ('scenario_type', 'is_template', 'is_deleted', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['target_node', 'created_by']
    fieldsets = (
        ('Scenario Information', {
            'fields': ('name', 'description', 'scenario_type', 'target_node')
        }),
        ('Parameters', {
            'fields': ('parameters',)
        }),
        ('Classification', {
            'fields': ('is_template', 'tags', 'created_by')
        }),
        ('Soft Delete', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SimulationRun)
class SimulationRunAdmin(admin.ModelAdmin):
    list_display = ('scenario', 'status_badge', 'started_at', 'execution_time_seconds', 'run_by')
    list_filter = ('status', 'started_at', 'run_by')
    search_fields = ('scenario__name', 'notes')
    readonly_fields = ('id', 'created_at', 'updated_at', 'execution_time_seconds')
    autocomplete_fields = ['scenario', 'run_by']
    date_hierarchy = 'started_at'
    fieldsets = (
        ('Simulation Details', {
            'fields': ('scenario', 'run_by')
        }),
        ('Execution', {
            'fields': ('started_at', 'completed_at', 'status', 'execution_time_seconds')
        }),
        ('Results', {
            'fields': ('results', 'notes')
        }),
        ('Errors', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'PENDING': 'gray',
            'RUNNING': 'blue',
            'COMPLETED': 'green',
            'FAILED': 'red',
            'CANCELLED': 'orange'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
