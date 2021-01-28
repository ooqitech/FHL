from django.db import models

from account.models import Department


# Create your models here.


class Project(models.Model):
    """
    Java 项目与 H5 项目
    """
    status = (
        (0, '不可用'),
        (1, '可用')
    )
    project_type = (
        (1, 'Java'),
        (2, 'Jar'),
        (3, 'H5')
    )

    name = models.CharField('应用名', max_length=50, unique=True, db_index=True)
    chinese_name = models.CharField(max_length=100, verbose_name='中文名称')
    department = models.ForeignKey(
        Department,
        models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='所属部门'
    )
    dev_group = models.ForeignKey(
        Department,
        models.SET_NULL,
        related_name='dev_group',
        blank=True,
        null=True,
        verbose_name='开发部门'
    )
    test_group = models.ForeignKey(
        Department,
        models.SET_NULL,
        related_name='test_group',
        blank=True,
        null=True,
        verbose_name='测试部门'
    )
    project_type = models.IntegerField(default=1, choices=project_type, verbose_name='项目类型')
    detail = models.CharField(max_length=200, verbose_name='项目描述')
    status = models.IntegerField(default=1, choices=status, verbose_name='项目状态')
    is_health = models.BooleanField('健康检查状况', default=True)
    is_root = models.BooleanField(default=False, verbose_name='war包名是否为ROOT')
    app_dir = models.CharField('应用目录', max_length=512, null=True, blank=True, default=None)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 't_project'
        ordering = ["create_time"]
