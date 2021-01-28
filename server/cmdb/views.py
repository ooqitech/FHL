import logging

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.response import Response

from core.authentication import Authentications
from core.permissions import module_permission
from projects.models import Project
from .api import app_to_ecs_host
from .models import ECSInstance, RDSDatabase, Staff
from .serializers import DatabaseSerializer, EcsSerializer, SimpleDatabaseSerializer, SimpleEcsSerializer, \
    StaffSerializer

logger = logging.getLogger('app')


# Create your views here.

class DatabaseViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = Authentications
    permission_classes = [module_permission('cmdb-database')]

    queryset = RDSDatabase.objects.all().order_by('-id')
    serializer_class = DatabaseSerializer

    filter_fields = ('db_name', 'instance_name',)

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_data = {k: v for k, v in self.request.query_params.items() if k in self.filter_fields}
        if filter_data:
            if 'db_name' in filter_data:
                db_name = filter_data.pop('db_name')
                queryset = queryset.filter(db__name__contains=db_name)
            if 'instance_name' in filter_data:
                instance_name = filter_data.pop('instance_name')
                queryset = queryset.filter(db_instance__name__contains=instance_name)
            queryset = queryset.filter(**filter_data)
        return queryset

    @action(methods=['get'], detail=False)
    def full(self, request, *args, **kwargs):
        """
        desc: 所有数据库信息（不分页）
        """
        _ = request, args, kwargs
        queryset = self.filter_queryset(self.get_queryset())

        serializer = SimpleDatabaseSerializer(queryset, many=True)
        return Response(serializer.data)


class EcsViewSet(viewsets.ModelViewSet):
    authentication_classes = Authentications
    permission_classes = [module_permission('cmdb-ecs')]

    queryset = ECSInstance.objects.all().order_by('-id')
    serializer_class = EcsSerializer

    http_method_names = ['get', 'patch']

    filter_fields = ('app_name', 'hostname', 'inner_ip_addr',)

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_data = {k: v for k, v in self.request.query_params.items() if k in self.filter_fields}
        if filter_data:
            if 'app_name' in filter_data:
                app_name = filter_data.pop('app_name')
                queryset = queryset.filter(app__name__contains=app_name)
            queryset = queryset.filter(**filter_data)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(app__isnull=False)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def idle(self, request, *args, **kwargs):
        """
        desc: 可用 IP 列表（用于绑定资源）
        """
        _ = request, args, kwargs
        queryset = self.get_queryset()
        queryset = queryset.filter(
            app__isnull=True,
            inner_ip_addr__regex=r'192\.168\.[0-9]{3}.*'
        ).values('id', 'inner_ip_addr')
        return Response(queryset)

    @action(methods=['get'], detail=False)
    def template(self, request, *args, **kwargs):
        """
        desc: 资源绑定模板文件下载
        """
        _ = request, args, kwargs
        response = HttpResponse()
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="ecs_template.csv"'
        response.write('应用名称,IP 地址'.encode('gb2312'))
        return response

    @action(methods=['patch'], detail=False)
    def batch_bind(self, request):
        """
        desc: 应用批量绑定资源
        input:
        - name: app_id
          desc: 应用 ID
          type: integer
        - name: ecs_list
          desc: ECS ID 列表
          type: list
        """
        try:
            app = Project.objects.get(id=request.data.get('app_id'))
        except Project.DoesNotExist:
            raise ValidationError({'app_id': '应用未找到'})
        failed = []
        ecs_list = request.data.get('ecs_list')
        if not ecs_list or not isinstance(ecs_list, list):
            raise ParseError({'ecs_list': '`ecs_list` 字段必须为 ECS ID 列表'})
        for ecs_id in ecs_list:
            try:
                ecs = ECSInstance.objects.get(id=ecs_id, app__isnull=True)
                ecs.app = app
                ecs.save()
            except ECSInstance.DoesNotExist:
                failed.append(ecs_id)
        if failed:
            raise ParseError({'ecs_list': f'以下 ECS 绑定失败: {failed}'})
        return Response({'message': '绑定成功'})

    @action(methods=['patch'], detail=False)
    def binds(self, request, *args, **kwargs):
        """
        desc: 资源批量绑定
        input:
        - name: file
          desc: 模板文件
          type: 文件
          required: true
        """
        _ = args, kwargs
        file = request.data.get('file')
        if not file or not isinstance(file, InMemoryUploadedFile):
            raise ValidationError({'file': '非法的资源文件'})
        failed, success = [], []
        data = file.read().decode('gb2312')
        for line in data.splitlines()[1:]:
            app_name, hostname = line.strip().split(',')
            try:
                ecs = ECSInstance.objects.get(inner_ip_addr=hostname, app__isnull=True)
                app = Project.objects.get(name=app_name)
                success.append((app, ecs,))
            except (ObjectDoesNotExist, MultipleObjectsReturned) as e:
                logger.error(f'绑定资源失败: {e}')
                failed.append((app_name, hostname,))
        if not failed:
            for app, ecs in success:
                ecs.app = app
                ecs.save()
            return Response({'message': '资源已绑定'})
        else:
            raise ParseError({'message': f'请注意，以下资源无法绑定，请检查: {failed}'})

    def partial_update(self, request, *args, **kwargs):
        """
        desc: 单个应用绑定资源
        input:
        - name: app_id
          type: integer
          desc: 应用 ID
        """
        try:
            app = Project.objects.get(id=request.data.get('app_id'))
            ecs = self.get_object()
            if ecs.app:
                raise ValidationError({'ecs': '该资源已被绑定，请检查'})
            ecs.app = app
            ecs.save()
        except ObjectDoesNotExist:
            raise ValidationError({'app_id': '未知应用，请检查'})

    @action(methods=['patch'], detail=True)
    def unbind(self, request, *args, **kwargs):
        """
        desc: 解绑资源
        """
        _ = request, args, kwargs
        ecs = self.get_object()
        ecs.app = None
        ecs.save()
        return Response({'message': '已解绑'})

    @action(methods=['get'], detail=False)
    def app_to_host(self, request, *args, **kwargs):
        """
        desc: 根据应用名/应用 ID (两者选择其中一个)获取绑定的主机列表
        input:
        - name: app_id
          type: integer
          desc: 应用 ID
          required: false
        - name: app_name
          type: string
          desc: 应用名
          required: false
        """
        _ = args, kwargs
        kwargs = dict(zip(request.query_params.keys(), request.query_params.values()))
        return Response(app_to_ecs_host(detail=True, **kwargs))


class ReadOnlyEcsViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = Authentications
    permission_classes = [module_permission('document')]

    queryset = ECSInstance.objects.all().order_by('-id')
    serializer_class = SimpleEcsSerializer

    def list(self, request, *args, **kwargs):
        """
        获取完整的 ecs 列表
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class StaffApiViewSet(viewsets.ModelViewSet):
    """
    create: 新建人员
    """
    authentication_classes = Authentications
    permission_classes = [module_permission('staff')]

    queryset = Staff.objects.all().order_by('-id')
    serializer_class = StaffSerializer
