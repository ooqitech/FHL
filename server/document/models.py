from django.db import models

from core.choices import JOB_STATUS_CHOICES


# Create your models here.

class Document(models.Model):
    """文件分发配置"""
    status = (
        (0, '未设置'),
        (1, '已设置'),
        (2, '已执行'),
    )

    name = models.CharField('文件名', max_length=200)
    md5 = models.CharField('文件 md5', max_length=200)
    operator = models.CharField(default='', max_length=200)
    payload = models.TextField('参数', default='')
    backup_path = models.CharField(null=True, default='', max_length=512)
    plan_time = models.DateTimeField(verbose_name='执行时间')
    status = models.IntegerField(default=0, choices=status)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_etcd_document'


class DocumentDistributeLog(models.Model):
    """文件分发记录"""
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    job_status = models.IntegerField(choices=JOB_STATUS_CHOICES)
    message = models.TextField(null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)

    class Meta:
        db_table = 't_etcd_document_distribute_log'


class RsyncFiles(models.Model):
    from account.models import SSHConfig
    src = models.CharField(max_length=256)
    dst = models.CharField(max_length=256)
    ssh = models.ForeignKey(
        SSHConfig,
        on_delete=models.CASCADE
    )
    job_status = models.IntegerField(default=0, choices=JOB_STATUS_CHOICES)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_rsync_files'
