import base64
import json
import re
from datetime import datetime
from hashlib import md5

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response

from core.authentication import Authentications
from core.permissions import module_permission
from .api import ETCD_FILE_TYPE, client, restore_document
from .models import Document, RsyncFiles
from .serializers import DocumentSerializer, RsyncSerializer


def validate_file(file):
    """验证文件"""
    if not file or not isinstance(file, InMemoryUploadedFile):
        raise ValidationError({'file': 'File required'})
    if file.name.split('.')[-1] not in ETCD_FILE_TYPE:
        raise ValidationError({'file': '不支持的文件类型'})
    if file.size > 1024 * 1024 * 5:  # 5MB
        raise ValidationError({'file': '文件超过 5MB，不能上传'})
    return file


class DocumentApiViewSet(viewsets.ModelViewSet):
    authentication_classes = Authentications
    permission_classes = [module_permission('document')]

    queryset = Document.objects.all().order_by('-id')
    serializer_class = DocumentSerializer
    http_method_names = ['get', 'post', 'delete']
    filter_fields = ['name', 'create_time', 'plan_time']

    @staticmethod
    def validate_plan_time(plan_time):
        """验证分发时间"""
        plan_time = datetime.strptime(plan_time, '%Y-%m-%d %H:%M:%S')
        now = datetime.now()
        if (plan_time - now).total_seconds() <= -5:
            raise ValidationError({'plan_time': '计划时间不能小于当前时间'})
        return plan_time

    def get_queryset(self):
        """
        可选过滤字段：`self.filter_fields`
        """
        queryset = Document.objects.all().order_by('-id')
        filter_data = {k: v for k, v in self.request.query_params.items() if k in self.filter_fields}
        if filter_data:
            if 'name' in filter_data:
                name = filter_data.pop('name')
                queryset = queryset.filter(name__contains=name)
            if 'create_time' in filter_data:
                year, month, day = filter_data.pop('create_time').split('-')
                queryset = queryset.filter(create_time__year=year, create_time__month=month, create_time__day=day)
            if 'plan_time' in filter_data:
                year, month = filter_data.pop('plan_time').split('-')
                queryset = queryset.filter(plan_time__year=year, plan_time__month=month)
            queryset = queryset.filter(**filter_data)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        desc: 文件上传
        input:
        - name: file
          desc: 要上传的配置文件
          type: file
        """
        file = validate_file(request.data.get('file'))
        plan_time = self.validate_plan_time(request.data.get('plan_time'))
        content = file.read()
        md5sum = md5(content).hexdigest()
        directory = f"{file.name.split('.')[-1]}/{md5sum}"
        content = base64.b64encode(content).decode('utf-8')
        response = client.put(key=file.name, value=content, directory=directory)
        if response.get('node'):
            instance = Document.objects.create(name=file.name, md5=md5sum, operator=request.user, plan_time=plan_time)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        raise APIException('文件上传 etcd 失败')

    @action(methods=['get'], detail=True)
    def download(self, request, pk=None):
        """文件下载"""
        _ = request, pk
        doc = self.get_object()
        directory = f"{doc.name.split('.')[-1]}/{doc.md5}"
        node = client.get(doc.name, directory=directory).get('node')
        if not node:
            raise APIException('文件未找到')
        content = base64.b64decode(node.get('value').encode('utf-8'))
        response = HttpResponse()
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f'attachment;filename="{doc.name}"'
        response.write(content)
        return response

    @staticmethod
    def validate_payload(payload):
        """验证分发参数"""
        if not payload:
            raise ValidationError({
                'payload': 'payload 不能为空'
            })
        if not payload.get('path'):
            raise ValidationError({
                'payload["path"]': '分发路径不能为空'
            })
        if not payload.get('servers') or not isinstance(payload['servers'], list):
            raise ValidationError({
                'payload["servers"]': '分发服务器为列表且不能为空'
            })
        if not re.match('^/[-_a-zA-Z0-9/]+$', payload.get('path') or re.search('/-|-/|-$', payload.get('path'))):
            raise ValidationError({
                'error': '目录必须为绝对路径且不能有空格等特殊符号！'
            })
        return payload

    @action(methods=['post'], detail=True)
    def distribute(self, request, pk=None):
        """
        desc: 配置文件分发
        input:
        - name: servers
          desc: 要分发的服务器 ID
          type: integer
        - name: path
          desc: 分发路径
          type: string
        - name: commands
          desc: 额外命令

        """

        _ = pk
        doc = self.get_object()

        payload = request.data.get('payload')
        status = bool(payload and payload.get('servers') and payload.get('path'))
        if payload and (not re.match('^/[-_a-zA-Z0-9/]+$', payload.get('path'))
                        or re.search('/-|-/|-$', payload.get('path'))):
            raise ValidationError({
                'error': '目录必须为绝对路径且不能有空格等特殊符号！'
            })
        doc.payload = json.dumps(payload)
        doc.status = status
        doc.save()

        return Response({'message': '已配置'})

    @action(methods=['post'], detail=True)
    def restore(self, request, pk=None):
        """文件恢复"""
        _ = request
        doc = self.get_object()
        log = doc.documentdistributelog_set.order_by('-id').first()
        if not log or log.job_status != 2 or log.job_status == 2 and log.message:
            raise ValidationError({'error': '不符合文件恢复的要求'})
        restore_document.delay(pk)
        return Response({'message': '开始文件恢复'})

    def perform_destroy(self, instance):
        md5sum = instance.md5
        if instance.status == 2:
            raise ValidationError('已分发配置不能被删除')
        if Document.objects.filter(md5=md5sum).count() == 1:
            directory = f"{instance.name.split('.')[-1]}/{md5sum}"
            client.delete(key=instance.name, directory=directory)
        return super().perform_destroy(instance)


class RsyncApiViewSet(viewsets.ModelViewSet):
    """
    create: 新建文件实时同步
    """
    authentication_classes = Authentications
    permission_classes = [module_permission('rsync')]

    queryset = RsyncFiles.objects.all().order_by('-id')
    serializer_class = RsyncSerializer
