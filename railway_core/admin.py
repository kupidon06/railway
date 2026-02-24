"""
Django admin configuration for railway_core models.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Node, Track, Train, Schedule, Event, Incident


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'node_type', 'capacity', 'track_count', 'is_deleted', 'created_at')
    list_filter = ('node_type', 'is_deleted', 'created_at')
    search_fields = ('code', 'name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'node_type', 'capacity', 'timezone')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
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

    def track_count(self, obj):
        return obj.tracks.filter(is_deleted=False).count()
    track_count.short_description = 'Active Tracks'


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('code', 'node', 'track_number', 'direction', 'status', 'max_speed_kmh', 'is_deleted')
    list_filter = ('status', 'direction', 'is_deleted', 'node')
    search_fields = ('code', 'name', 'node__code', 'node__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['node']
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'node', 'track_number')
        }),
        ('Configuration', {
            'fields': ('length_meters', 'max_speed_kmh', 'direction', 'status')
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


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ('train_number', 'train_type', 'operator', 'capacity_passengers', 'max_speed_kmh', 'is_deleted')
    list_filter = ('train_type', 'operator', 'is_deleted', 'created_at')
    search_fields = ('train_number', 'operator')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('train_number', 'train_type', 'operator')
        }),
        ('Specifications', {
            'fields': ('capacity_passengers', 'length_meters', 'max_speed_kmh')
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


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'train',
        'node',
        'track',
        'scheduled_arrival',
        'scheduled_departure',
        'status_badge',
        'delay_minutes'
    )
    list_filter = ('status', 'node', 'scheduled_arrival', 'is_deleted')
    search_fields = ('train__train_number', 'node__code', 'node__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['train', 'node', 'track']
    date_hierarchy = 'scheduled_arrival'
    fieldsets = (
        ('Train & Location', {
            'fields': ('train', 'node', 'track')
        }),
        ('Schedule', {
            'fields': (
                ('scheduled_arrival', 'scheduled_departure'),
                ('actual_arrival', 'actual_departure'),
                'status',
                'delay_minutes'
            )
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
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

    def status_badge(self, obj):
        colors = {
            'SCHEDULED': 'gray',
            'ON_TIME': 'green',
            'DELAYED': 'orange',
            'CANCELLED': 'red',
            'COMPLETED': 'blue'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'event_type', 'severity_badge', 'train', 'node', 'track')
    list_filter = ('event_type', 'severity', 'node', 'timestamp')
    search_fields = ('description', 'train__train_number', 'node__code')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['train', 'node', 'track']
    date_hierarchy = 'timestamp'
    fieldsets = (
        ('Event Details', {
            'fields': ('timestamp', 'event_type', 'severity', 'description')
        }),
        ('Related Entities', {
            'fields': ('train', 'node', 'track')
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

    def severity_badge(self, obj):
        colors = {
            'INFO': 'blue',
            'WARNING': 'orange',
            'CRITICAL': 'red'
        }
        color = colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'incident_type',
        'severity_badge',
        'node',
        'status',
        'started_at',
        'duration_display'
    )
    list_filter = ('incident_type', 'severity', 'status', 'node', 'started_at', 'is_deleted')
    search_fields = ('title', 'description', 'node__code', 'node__name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'duration_display')
    autocomplete_fields = ['node', 'affected_trains']
    filter_horizontal = ('affected_tracks', 'affected_trains')
    date_hierarchy = 'started_at'
    fieldsets = (
        ('Incident Details', {
            'fields': ('title', 'description', 'incident_type', 'severity', 'status')
        }),
        ('Location & Impact', {
            'fields': ('node', 'affected_tracks', 'affected_trains')
        }),
        ('Timeline', {
            'fields': ('started_at', 'resolved_at', 'duration_display')
        }),
        ('Resolution', {
            'fields': ('reported_by', 'resolution_notes'),
            'classes': ('collapse',)
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

    def severity_badge(self, obj):
        colors = {
            'LOW': 'green',
            'MEDIUM': 'orange',
            'HIGH': 'red',
            'CRITICAL': 'darkred'
        }
        color = colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'

    def duration_display(self, obj):
        duration = obj.get_duration()
        hours = duration // 60
        minutes = duration % 60
        return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
    duration_display.short_description = 'Duration'


# Enable autocomplete for Node model
Node.autocomplete_fields = []
