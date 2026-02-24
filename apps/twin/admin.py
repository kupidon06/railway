"""
Django admin configuration for railway_twin models.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import TrainPosition
from apps.core.models import Train, Node, Track


@admin.register(TrainPosition)
class TrainPositionAdmin(admin.ModelAdmin):
    list_display = ('train', 'current_node', 'current_track', 'status_badge', 'speed_kmh', 'timestamp')
    list_filter = ('status', 'current_node', 'timestamp')
    search_fields = ('train__train_number', 'current_node__code', 'current_node__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['train', 'current_node', 'current_track']
    date_hierarchy = 'timestamp'
    fieldsets = (
        ('Train & Location', {
            'fields': ('train', 'timestamp', 'current_node', 'current_track')
        }),
        ('GPS Coordinates', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Movement Data', {
            'fields': ('speed_kmh', 'status')
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

    def status_badge(self, obj):
        colors = {
            'MOVING': 'green',
            'STOPPED': 'orange',
            'BOARDING': 'blue',
            'MAINTENANCE': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
