from django.db import models

from projects.models import Project


# Create your models here.

class ECSInstance(models.Model):
    app = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='ecs 关联应用'
    )
    inner_ip_addr = models.CharField('内网 IP', max_length=64)
    outer_ip_addr = models.CharField('公网 IP', max_length=64, default='')
    outer_bandwidth = models.IntegerField('带宽', null=True)
    elastic_ip = models.CharField(null=True, max_length=64)
    hostname = models.CharField('主机名', max_length=128)
    cpu_count = models.IntegerField('CPU 核心数', default=1)
    memory_size = models.IntegerField('内存大小', default=2048)
    disk_size = models.IntegerField(default=60)
    location = models.CharField(default='hangzhou-east-1', max_length=64)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_ecs_instance'


class RDSInstance(models.Model):
    """RDS 实例"""

    name = models.CharField('实例名', max_length=64)
    db_engine = models.CharField(max_length=64)
    db_description = models.CharField('实例详情', max_length=64)
    db_connection = models.CharField(max_length=300, default=None)
    is_online = models.BooleanField('是否在线', default=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_rds_instance'


class RDSDatabase(models.Model):
    """RDS 数据库信息"""
    db_name = models.CharField(max_length=64)
    db_instance = models.ForeignKey(
        RDSInstance,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='关联 RDS 实例'
    )
    db_engine = models.CharField(max_length=64)
    is_online = models.BooleanField(default=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_rds_database'


class LoadBalancers(models.Model):
    """
    负载均衡实例
    """
    slb_id = models.CharField(max_length=200, unique=True)
    ip_addr = models.CharField(max_length=64)
    ports = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_slb'


class SLBBackendServers(models.Model):
    """
    负载均衡后端服务器
    """
    lb_id = models.CharField(max_length=200)
    ip_addr = models.CharField(max_length=64)
    port = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_slb_backend_servers'


class Staff(models.Model):
    """
    人员
    """
    name = models.CharField(max_length=64)
    email = models.CharField(max_length=128)
    phone = models.CharField(max_length=32)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_staff'
