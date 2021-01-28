"""
权限初始化
"""
import logging

from .models import Permission

logger = logging.getLogger('app')


def main():
    permissions = {
        'projects': '项目管理',
        'document': '文件分发',
        'repo': '仓库',
        'cmdb-database': '数据库',
        'cmdb-ecs': 'ecs',
        'command': '服务器命令执行',
        'rsync': '文件同步',
        'staff': '人员管理',
    }

    for name, desc in permissions.items():
        if not Permission.objects.filter(name=name).first():
            Permission.objects.create(name=name, desc=desc)
            logger.info(f'初始化权限 {name} 成功')
