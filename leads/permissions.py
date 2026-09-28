from rest_framework import permissions

class IsStaffOrAssignedUser(permissions.BasePermission):
    """
    Staff can do anything. Regular users can view or edit only leads assigned to them.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.assigned_to == request.user or obj.assigned_to is None
