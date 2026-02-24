class SoftDeleteQuerySetMixin:
    """Filters out soft-deleted objects by default."""

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(qs.model, 'is_deleted'):
            include_deleted = (
                self.request.query_params.get('include_deleted', 'false').lower() == 'true'
            )
            if include_deleted and self.request.user.is_superuser:
                return qs
            return qs.filter(is_deleted=False)
        return qs


class SoftDeleteDestroyMixin:
    """Override destroy() to perform soft-delete."""

    def perform_destroy(self, instance):
        if hasattr(instance, 'soft_delete'):
            instance.soft_delete()
        else:
            instance.delete()
