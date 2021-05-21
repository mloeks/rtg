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
        return request.user.is_staff or (request.user.is_authenticated and request.method in permissions.SAFE_METHODS)


class IsAdminOrOwner(permissions.BasePermission):
    """
        Allow unsafe methods for admin users and owners of the instance only.
        Allow safe methods for authenticated users only.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            else:
                return request.user.is_staff or obj.user == request.user


class IsAdminOrSelf(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            else:
                return request.user.is_staff or obj == request.user


class PostPermissions(permissions.BasePermission):
    """
        Every authenticated user may create or read posts. They may only delete their own posts.
        Only admins may specify the properties that make posts being sent as e-mail.
        Admins may generally use all HTTP methods on all posts.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_staff or request.method in permissions.SAFE_METHODS or request.method == 'DELETE':
                return True
            return self._is_write_request_without_mail_options(request)
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if request.user.is_staff or request.method in permissions.SAFE_METHODS:
                return True
            if request.method == 'DELETE' and request.user.pk == obj.author.pk:
                return True
            return self._is_write_request_without_mail_options(request)
        else:
            return False

    def _is_write_request_without_mail_options(self, request):
        return request.method in ['POST', 'PATCH'] and not self._request_contains_mail_options(request)

    def _request_contains_mail_options(self, request):
        return 'as_mail' in request.data or 'force_active_users' in request.data \
                    or 'force_inactive_users' in request.data \
                    or 'force_all_users' in request.data


class CommentPermissions(permissions.BasePermission):
    """
        Every authenticated user may create or read comments.
        Admins may use all HTTP methods.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_staff or request.method in permissions.SAFE_METHODS or request.method == 'POST'
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return request.user.is_staff or request.method in permissions.SAFE_METHODS or request.method == 'POST'
        else:
            return False


class UserPermissions(permissions.BasePermission):
    """
        Permissions for (complete) UserViewSet.
        List access is read-only (safe methods) for authenticated users.
        Object access is only permitted for the owner or an Administrator.
        POSTing a new User should only be allowed for admin users.
        DELETing a User should only be allowed for admins or the owner.
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            if user.is_staff:
                return True
            else:
                return request.method in permissions.SAFE_METHODS or \
                       (request.method in ['PUT', 'PATCH', 'DELETE'] and self.is_own_user_resource(user, view))
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (request.user.is_staff or obj == request.user)

    def is_own_user_resource(self, user, view):
        return view.queryset.filter(username=user.username).exists()
