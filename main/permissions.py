__author__ = 'mloeks'

from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAdminOrAuthenticatedReadOnly(permissions.BasePermission):
    """
        Allow unsafe methods for admin users only.
        Allow safe methods for authenticated users only.
    """

    def has_permission(self, request, view):
        return request.user.is_staff or (request.user.is_authenticated() and request.method in permissions.SAFE_METHODS)


class IsAdminOrOwner(permissions.BasePermission):
    """
        Allow unsafe methods for admin users and owners of the instance only.
        Allow safe methods for authenticated users only.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated():
            if request.method in permissions.SAFE_METHODS:
                return True
            else:
                return request.user.is_staff or obj.user == request.user


class IsAdminOrSelf(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated():
            if request.method in permissions.SAFE_METHODS:
                return True
            else:
                return request.user.is_staff or obj == request.user


class IsAdminOrSelfUpdateOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        permitted_methods = permissions.SAFE_METHODS + ('PUT', 'PATCH')
        return request.user.is_authenticated() and request.method in permitted_methods

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated():
            if request.method in permissions.SAFE_METHODS:
                return True
            elif request.method in ['PUT', 'PATCH']:
                return request.user.is_staff or obj == request.user or (hasattr(obj, 'user') and obj.user == request.user)
            else:
                return False


class UserPermissions(permissions.BasePermission):
    """
        Permissions for (complete) UserViewSet.
        List access is read-only (safe methods) for authenticated users.
        Object access is only permitted for the owner or an Administrator.
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            if user.is_staff:
                return True
            else:
                return request.method in permissions.SAFE_METHODS or \
                       (request.method in ['PUT', 'PATCH'] and self.is_own_user_resource(user, view))
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (request.user.is_staff or obj == request.user)

    def is_own_user_resource(self, user, view):
        return view.queryset.filter(username=user.username).exists()
