"""
权限模块
"""
from rest_framework import permissions

from account.models import User


class AccountPermission(permissions.BasePermission):
    """
    账户权限，个人用户仅有查看、编辑自己的信息两个权限，管理员开放所有权限
    """

    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated):
            return False
        return request.user.is_staff or request.user.is_superuser or request.method in ('GET', 'PUT', 'PATCH')

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser or request.method in permissions.SAFE_METHODS:
            return True

        return request.method in ('PUT', 'PATCH') and obj == request.user


def module_permission(module: str, read_only=False, module_user_read_only=False):
    """
    根据名字 module 产生对应权限的类
    Args:
        module: 模块名
        read_only: 其他登录用户是否可读
        module_user_read_only: 该模块权限用户可读

    Returns:
        对应权限类
    """

    def is_module_user(user: User):
        """判断用户所在组或部门是否有相应权限"""
        if user.department and user.department.permissions.filter(name=module):
            return True
        if not user.group:
            return False
        for department in user.group.departments.all():
            if department.permissions.filter(name=module):
                return True
        return False

    class ModulePermission(permissions.BasePermission):
        """
        模块级权限
        """

        def has_permission(self, request, view):
            # 未登录
            if not (request.user and request.user.is_authenticated):
                return False

            # 管理员
            if request.user.is_staff or request.user.is_superuser:
                return True

            # 其他用户只读
            if request.method == 'GET' and read_only:
                return True

            # 模块级用户只读
            if module_user_read_only:
                return request.method == 'GET' and is_module_user(request.user)

            return is_module_user(request.user)

    return ModulePermission


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    非管理员的登录用户有可读权限
    """

    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated):
            return False
        return request.method in permissions.SAFE_METHODS or request.user.is_staff or request.user.is_superuser
