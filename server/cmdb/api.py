from projects.models import Project
from .models import ECSInstance


def app_to_ecs_host(app_id=None, app_name=None, detail=False) -> list:
    """
    根据应用 ID 获取对应的机器列表
    Args:
        app_id: 应用 ID
        app_name: 应用名
        detail: 是否包含 ECS ID

    Returns:
        list: 机器列表
    """
    if not any([app_id, app_name]):
        return []
    if app_id is None:
        app = Project.objects.filter(name=app_name).first()
        if not app:
            return []
        app_id = app.id

    if detail:
        return list(ECSInstance.objects.filter(
            app_id=app_id,
            app__isnull=False
        ).all().values('id', 'app_id', 'inner_ip_addr', 'hostname'))
    return [ecs.inner_ip_addr for ecs in ECSInstance.objects.filter(app_id=app_id, app__isnull=False).all()]
