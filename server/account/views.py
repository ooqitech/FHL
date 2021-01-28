from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import Authentications
from core.permissions import AccountPermission, IsAdminOrReadOnly
from utils.crypto import decrypt, encrypt
from .models import AliyunConfig, Department, Group, Permission, SSHConfig, SystemConfig, User
from .serializers import (AliyunConfigSerializer, DepartmentSerializer, GroupSerializer, PermissionSerializer,
                          ReadOnlyDepartmentSerializer, ReadOnlyUserSerializer, SSHConfigSerializer,
                          SystemConfigSerializer, UserSerializer)


# Create your views here.

class UserPasswordResetApiView(APIView):
    """
    配置确认接口
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """修改密码界面"""
        try:
            decrypt(request.query_params.get('key'))
        except Exception:
            raise ValidationError(f'无效的 Key')

        return Response('not implemented')

    def post(self, request):
        """
        desc: 请求修改密码
        input:
        - name: username
          desc: 用户名
          type: string
          required: true
        - name: email
          desc: 用户邮箱
          type: string
          required: true
        """

        user = User.objects.filter(username=request.data.get('username'), email=request.data.get('email')).first()
        if not user:
            raise ValidationError({'error': '用户名或邮箱无效'})

        token = Token.objects.get(user=user)
        user.request_reset_password(encrypt(token.key))

        return Response({'message': 'Success'})

    def put(self, request):
        """
        desc: 修改密码
        input:
        - name: password
          desc: 新密码
          type: string
          required: true
        """
        try:
            key = decrypt(request.data.get('key'))
        except Exception:
            raise ValidationError({'key': 'key 已失效'})
        token = Token.objects.filter(key=decrypt(key)).first()
        if not token:
            raise ValidationError({'error': '该链接已失效'})
        user = token.user
        password = request.data.get('password', '').strip()
        if not password:
            raise ValidationError({'password': '密码不能为空'})
        user.set_password(password)
        token.delete()
        user.save()


class UserApiViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        返回一个用户实例

    list:
        返回所有用户列表

    create:
        创建用户

    delete:
        删除用户

    partial_update:
        同 Update

    update:
        更新用户信息
    """
    authentication_classes = Authentications
    permission_classes = [AccountPermission]

    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_superuser:
            queryset = queryset.filter(username=request.user.username)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['put'], detail=True)
    def set_password(self, request, pk=None):
        """
        desc: 设置用户密码
        input:
        - name: password
          desc: 用户密码
          type: string
          required: true
        """
        _ = pk
        user = self.get_object()
        password = request.data.get('password', '').strip()
        if not password:
            raise ValidationError({'password': '密码不能为空'})
        user.set_password(password)
        user.save()
        return Response({'message': 'Success'})

    @action(methods=['patch'], detail=True)
    def set_department(self, request, pk=None):
        """
        desc: 修改/设置部门
        input:
        - name: department_id
          desc: 部门 ID
          type: integer
          required: true
        """
        _ = pk
        user = self.get_object()
        department = Department.objects.get(id=request.data.get('department_id'))
        user.department = department
        user.save()
        return Response({'message': 'Success'})


class DepartmentApiViewSet(viewsets.ModelViewSet):
    authentication_classes = Authentications
    permission_classes = [IsAdminOrReadOnly]

    queryset = Department.objects.all().order_by('-id')
    serializer_class = DepartmentSerializer

    def perform_destroy(self, instance):
        if instance.user_set.all():
            raise ParseError('该部门还有关联用户，请先解绑用户后再删除')
        return super().perform_destroy(instance)

    @action(methods=['post'], detail=True)
    def permission(self, request, pk=None):
        """
        desc: 部门添加权限
        input:
        - name: permission
          desc: 权限 ID
          type: integer
          required: true
        """
        _ = pk
        department = self.get_object()
        permission = Permission.objects.get(id=request.data.get('permission'))
        department.permissions.add(permission)
        department.save()
        return Response({'message': 'Success'})


class PermissionApiViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = Authentications
    permission_classes = [IsAdminUser]

    queryset = Permission.objects.all().order_by('-id')
    serializer_class = PermissionSerializer


class GroupApiViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        返回一个组实例

    list:
        返回所有组列表

    create:
        创建组，departments 可选（部门 ID 列表）

    delete:
        删除组

    partial_update:
        同 Update

    update:
        更新组信息
    """
    authentication_classes = Authentications
    permission_classes = [IsAdminUser]

    queryset = Group.objects.all().order_by('-id')
    serializer_class = GroupSerializer

    @action(methods=['post'], detail=True)
    def bind_user(self, request, *args, **kwargs):
        """
        desc: 单个用户绑定组
        input:
        - name: user_id
          type: integer
          desc: 用户 ID
          required: true
        """
        _, _ = args, kwargs
        group = self.get_object()
        user = User.objects.get(id=request.data.get('user_id'))
        group.user_set.add(user)
        group.save()
        return Response({'message': '绑定成功'})

    @action(methods=['post'], detail=True)
    def add_users(self, request, *args, **kwargs):
        """
        desc: 同时绑定多个用户
        input:
        - name: users
          type: list
          desc: 用户 ID 列表
          required: true
        """
        _, _ = args, kwargs
        group = self.get_object()
        for user_id in request.data.get('users'):
            user = User.objects.get(id=user_id)
            group.user_set.add(user)
        group.save()

        return Response({'message': '绑定成功'})

    @action(methods=['post'], detail=True)
    def bind_department(self, request, *args, **kwargs):
        """
        desc: 部门绑定组
        input:
        - name: departments
          type: list
          desc: 部门 ID 列表
          required: true
        """
        _, _ = args, kwargs
        group = self.get_object()
        for department_id in request.data.get('departments'):
            dp = Department.objects.get(id=department_id)
            group.departments.add(dp)
        group.save()

        return Response({'message': '绑定成功'})

    def perform_destroy(self, instance):
        if instance.user_set.all():
            raise ParseError('该组还有关联用户，请先解绑用户后再删除')
        return super().perform_destroy(instance)


class ReadOnlyUserApiViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = Authentications
    permission_classes = [IsAuthenticated]

    queryset = User.objects.all().order_by('-id')
    serializer_class = ReadOnlyUserSerializer

    def list(self, request, *args, **kwargs):
        """不分页用户列表，仅有用户 ID 与用户名字段"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ReadOnlyDepartmentApiViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = Authentications
    permission_classes = [IsAuthenticated]

    queryset = Department.objects.all().order_by('-id')
    serializer_class = ReadOnlyDepartmentSerializer

    def list(self, request, *args, **kwargs):
        """不分页部门列表"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SystemConfigApiViewSet(viewsets.ModelViewSet):
    authentication_classes = Authentications
    permission_classes = [AllowAny]

    queryset = SystemConfig.objects.all().order_by('-id')
    serializer_class = SystemConfigSerializer

    @action(methods=['get'], detail=False)
    def default(self, request):
        _ = request
        queryset = self.get_queryset().first()
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)


class AliyunConfigApiViewSet(viewsets.ModelViewSet):
    authentication_classes = Authentications
    permission_classes = [IsAdminUser]

    queryset = AliyunConfig.objects.all().order_by('-id')
    serializer_class = AliyunConfigSerializer


class SSHConfigApiViewSet(viewsets.ModelViewSet):
    authentication_classes = Authentications
    permission_classes = [IsAdminUser]

    queryset = SSHConfig.objects.all().order_by('-id')
    serializer_class = SSHConfigSerializer
