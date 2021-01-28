from django.db.models import QuerySet

from account.models import User
from .models import Project


def get_projects(user: User) -> QuerySet:
    """
    根据用户及用户所在组筛选出对应的项目
    """
    if user.is_superuser or user.is_staff:
        return Project.objects.order_by('-id').all()
    dps = []
    if user.department:
        dps.append(user.department)
    if user.group:
        dps += list(user.group.departments.all())
    return Project.objects.filter(department__in=dps).order_by('-id').all()
