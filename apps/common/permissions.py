"""
Permission helpers for Railway Digital Twin RBAC (Role-Based Access Control).

Adapted from djengooCalendar Membership permission patterns.
"""
from django.core.exceptions import PermissionDenied


class RailwayPermissions:
    """
    Central permission checker for Railway operations.

    Roles:
    - ADMIN: Full system access
    - OPERATOR: View dashboard, manage incidents, run simulations, acknowledge alerts
    - ANALYST: View dashboard, run simulations (read-only), view reports
    - VIEWER: View dashboard only (read-only)
    - API_USER: Programmatic API access
    """

    # Role constants
    ADMIN = 'ADMIN'
    OPERATOR = 'OPERATOR'
    ANALYST = 'ANALYST'
    VIEWER = 'VIEWER'
    API_USER = 'API_USER'

    @staticmethod
    def can_view_dashboard(user):
        """All authenticated users can view the dashboard."""
        return user.is_authenticated

    @staticmethod
    def can_manage_nodes(user):
        """Check if user can create/update/delete nodes."""
        if user.is_superuser:
            return True
        return hasattr(user, 'role') and user.role in [
            RailwayPermissions.ADMIN,
            RailwayPermissions.OPERATOR
        ]

    @staticmethod
    def can_manage_schedules(user):
        """Check if user can modify schedules."""
        if user.is_superuser:
            return True
        return hasattr(user, 'role') and user.role in [
            RailwayPermissions.ADMIN,
            RailwayPermissions.OPERATOR
        ]

    @staticmethod
    def can_run_simulation(user):
        """Check if user can execute simulations."""
        if user.is_superuser:
            return True
        return hasattr(user, 'role') and user.role in [
            RailwayPermissions.ADMIN,
            RailwayPermissions.OPERATOR,
            RailwayPermissions.ANALYST
        ]

    @staticmethod
    def can_manage_incidents(user):
        """Check if user can create/update incidents."""
        if user.is_superuser:
            return True
        return hasattr(user, 'role') and user.role in [
            RailwayPermissions.ADMIN,
            RailwayPermissions.OPERATOR
        ]

    @staticmethod
    def can_acknowledge_alerts(user):
        """Check if user can acknowledge alerts."""
        if user.is_superuser:
            return True
        return hasattr(user, 'role') and user.role in [
            RailwayPermissions.ADMIN,
            RailwayPermissions.OPERATOR
        ]

    @staticmethod
    def can_view_reports(user):
        """Check if user can view reports."""
        if user.is_superuser:
            return True
        return hasattr(user, 'role') and user.role in [
            RailwayPermissions.ADMIN,
            RailwayPermissions.OPERATOR,
            RailwayPermissions.ANALYST
        ]

    @staticmethod
    def can_manage_users(user):
        """Check if user can manage other users."""
        return user.is_superuser or (hasattr(user, 'role') and user.role == RailwayPermissions.ADMIN)

    @staticmethod
    def check_permission(user, permission_name):
        """
        Generic permission checker that raises PermissionDenied if check fails.

        Args:
            user: The user to check permissions for
            permission_name: Name of permission method (e.g., 'can_run_simulation')

        Raises:
            PermissionDenied: If user doesn't have the required permission
        """
        permission_method = getattr(RailwayPermissions, permission_name, None)
        if permission_method is None:
            raise ValueError(f"Unknown permission: {permission_name}")

        if not permission_method(user):
            raise PermissionDenied(f"You don't have permission to {permission_name.replace('can_', '')}")
