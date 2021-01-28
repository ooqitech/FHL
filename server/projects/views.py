from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.authentication import Authentications
from core.permissions import module_permission
from projects.api import get_projects
from .models import Project
from .serializers import ProjectSerializer, SimpleProjectSerializer


class ProjectApiViewSet(viewsets.ModelViewSet):
    authentication_classes = Authentications
    permission_classes = [module_permission('projects')]

    queryset = Project.objects.all().order_by('-id')
    serializer_class = ProjectSerializer

    filter_fields = ('project_type', 'app_name', 'department', 'is_root', 'name')

    def get_queryset(self):
        """
        可选过滤字段：self.filter_fields
        """
        queryset = get_projects(self.request.user)
        filter_data = {k: v for k, v in self.request.query_params.items() if k in self.filter_fields}
        if filter_data:
            if 'app_name' in filter_data:
                app_name = filter_data.pop('app_name')
                queryset = queryset.filter(name__contains=app_name)
            queryset = queryset.filter(**filter_data)

        return queryset

    def list(self, request, *args, **kwargs):
        """获取项目列表"""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        desc: 创建新项目
        input:
        - name: name
          desc: 应用名
          required: true
        - name chinese_name
          desc: 应用中文名
          required: True
        - name: detail
          desc: 应用详情
          required: True
        - name: department_id
          desc: 所属部门 ID
          type: integer
        - name: dev_group_id
          desc：开发部门 ID
          type: integer
        - name: test_group_id
          desc: 测试部门 ID
          type: integer
        - name: is_root
          desc: 是否为 Root 包，Java 应用需要
        - name: app_dir
          desc: 应用路径，H5 应用需要
        """

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        desc: 更新项目
        """
        kwargs['partial'] = True
        _full_data = request.data.copy()
        _full_data['name'] = self.get_object().name
        request._full_data = _full_data
        return super().update(request, *args, **kwargs)

    @action(methods=['get'], detail=False)
    def chinese_name(self, request, *args, **kwargs):
        """
        desc: 获取应用中文名
        input:
        - name: name
          desc: 应用名
          required: True
        """
        _ = args, kwargs
        try:
            cname = Project.objects.get(name=request.query_params.get('name')).chinese_name
        except Project.DoesNotExist:
            cname = request.query_params.get('name')
        return Response({'chinese_name': cname})

    def retrieve(self, request, *args, **kwargs):
        """获取单个项目信息"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        return Response(data)

    def perform_destroy(self, instance: Project):
        if instance.ecsinstance_set.all():
            raise ParseError({'应用已绑定 ECS，请解绑后再删除'})

        return super().perform_destroy(instance)


class PublicProjectApiViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = Authentications
    permission_classes = [IsAuthenticated]

    queryset = Project.objects.all().order_by('-id')
    serializer_class = SimpleProjectSerializer

    filter_fields = ('project_type', 'app_name', 'name')

    def get_queryset(self):
        queryset = get_projects(self.request.user)
        filter_data = {k: v for k, v in self.request.query_params.items() if k in self.filter_fields}
        if filter_data:
            if 'app_name' in filter_data:
                app_name = filter_data.pop('app_name')
                queryset = queryset.filter(name__contains=app_name)
            queryset = queryset.filter(**filter_data)
        return queryset

    def list(self, request, *args, **kwargs):
        """项目列表，不分页"""
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
