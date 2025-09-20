from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    All other users (including anonymous) can view objects.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to admin users.
        return request.user and request.user.is_staff and request.user.is_authenticated
