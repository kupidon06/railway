from rest_framework.permissions import BasePermission
from .permissions import RailwayPermissions


class CanManageNodes(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user.is_authenticated
        return RailwayPermissions.can_manage_nodes(request.user)


class CanManageSchedules(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user.is_authenticated
        return RailwayPermissions.can_manage_schedules(request.user)


class CanManageIncidents(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user.is_authenticated
        return RailwayPermissions.can_manage_incidents(request.user)


class CanRunSimulation(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user.is_authenticated
        return RailwayPermissions.can_run_simulation(request.user)


class CanAcknowledgeAlerts(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user.is_authenticated
        return RailwayPermissions.can_acknowledge_alerts(request.user)


class CanViewReports(BasePermission):
    def has_permission(self, request, view):
        return RailwayPermissions.can_view_reports(request.user)


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user.is_authenticated
        return RailwayPermissions.can_manage_users(request.user)
