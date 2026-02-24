"""
Django admin configuration for railway_analytics models.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'alert_type',
        'severity_badge',
        'node',
        'train',
        'status_display',
        'created_at'
    )
    list_filter = ('alert_type', 'severity', 'is_acknowledged', 'is_dismissed', 'created_at')
    search_fields = ('title', 'message', 'node__code', 'train__train_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['node', 'train', 'incident', 'acknowledged_by']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Alert Details', {
            'fields': ('alert_type', 'severity', 'title', 'message')
        }),
        ('Related Entities', {
            'fields': ('node', 'train', 'incident')
        }),
        ('Acknowledgement', {
            'fields': (
                'is_acknowledged',
                'acknowledged_by',
                'acknowledged_at',
                'acknowledgement_notes'
            )
        }),
        ('Auto-Dismissal', {
            'fields': ('auto_dismiss_at', 'is_dismissed', 'dismissed_at'),
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

    def status_display(self, obj):
        if obj.is_dismissed:
            return format_html(
                '<span style="color: gray;">Dismissed</span>'
            )
        elif obj.is_acknowledged:
            return format_html(
                '<span style="color: green;">✓ Acknowledged</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠ Active</span>'
            )
    status_display.short_description = 'Status'

    actions = ['acknowledge_alerts', 'dismiss_alerts']

    def acknowledge_alerts(self, request, queryset):
        for alert in queryset:
            if not alert.is_acknowledged:
                alert.acknowledge(request.user, notes='Acknowledged via admin action')
        self.message_user(request, f"{queryset.count()} alert(s) acknowledged.")
    acknowledge_alerts.short_description = "Acknowledge selected alerts"

    def dismiss_alerts(self, request, queryset):
        for alert in queryset:
            if not alert.is_dismissed:
                alert.dismiss()
        self.message_user(request, f"{queryset.count()} alert(s) dismissed.")
    dismiss_alerts.short_description = "Dismiss selected alerts"
