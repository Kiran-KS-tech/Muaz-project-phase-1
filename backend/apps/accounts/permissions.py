from rest_framework import permissions
from .models import User


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == User.Roles.SUPER_ADMIN


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == User.Roles.OWNER


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == User.Roles.MANAGER


class IsSuperAdminOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                request.user.role in [User.Roles.SUPER_ADMIN, User.Roles.OWNER])


class IsManagerOrAbove(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                request.user.role in [User.Roles.SUPER_ADMIN, User.Roles.OWNER, User.Roles.MANAGER])


class IsDriver(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == User.Roles.DRIVER
