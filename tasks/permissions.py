from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrAdmin(BasePermission):
    """Allow owners full access; admins can do anything; others read-only on SAFE methods."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return user and (user.is_staff or obj.owner_id == getattr(user, "id", None))