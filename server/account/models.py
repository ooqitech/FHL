from django.contrib.auth.models import AbstractUser
from django.db import models

from utils.crypto import decrypt
from utils.email import send_email


# Create your models here.


class Permission(models.Model):
    """部门权限"""
    name = models.CharField('权限名', unique=True, max_length=128)
    desc = models.CharField('权限描述', max_length=256, default='')

    def __str__(self):
        return self.name


class Department(models.Model):
    """部门"""
    name = models.CharField('部门名', unique=True, max_length=64)
    detail = models.CharField(max_length=64, default='')
    email = models.EmailField(max_length=255, null=True, verbose_name='部门邮箱')
    desc = models.CharField(max_length=256, null=True, blank=True)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
    )

    def __str__(self):
        return self.name


class Group(models.Model):
    """
    用户组，用于关联部门
    """

    departments = models.ManyToManyField(
        Department,
        blank=True
    )
    name = models.CharField('组名', max_length=64)
    desc = models.CharField('组信息', max_length=256, null=True, blank=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    phone = models.CharField('手机号', max_length=20)
    department = models.ForeignKey(
        Department,
        models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='用户所在部门'
    )
    group = models.ForeignKey(
        Group,
        models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='用户组'
    )

    def email_user(self, subject, message, **kwargs):
        """发送邮件给当前用户"""
        send_email(email_to=self.email, subject=subject, contents=message)

    def request_reset_password(self, encrypted_key):
        """请求重置密码，发送邮件获取链接"""
        subject = f'密码重置'
        content = f'{encrypted_key}'
        send_email(email_to=[self.email], subject=subject, contents=content)


class SystemConfig(models.Model):
    """系统配置"""
    name = models.CharField('系统名', max_length=64, unique=True, null=False)
    logo = models.ImageField('Logo', upload_to='logo', null=False)
    in_use = models.BooleanField('是否默认', default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AliyunConfig(models.Model):
    """阿里云账号配置"""
    key = models.CharField('阿里云登录 Key', max_length=256, null=False)
    secret = models.CharField('阿里云登录 Secret', max_length=256, null=False)
    region = models.CharField('阿里云 Region', max_length=256, null=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class SSHConfig(models.Model):
    hostname = models.CharField(max_length=64, unique=True)
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=256)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    @property
    def raw_password(self):
        return decrypt(self.password)
