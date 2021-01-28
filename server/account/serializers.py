import socket

from rest_framework import serializers

from utils.crypto import encrypt
from .models import AliyunConfig, Department, Group, Permission, SSHConfig, SystemConfig, User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    department_name = serializers.ReadOnlyField(source='department.name')
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    group_name = serializers.ReadOnlyField(source='group.name')

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'phone',
            'email',
            'date_joined',
            'last_login',
            'department',
            'group',
            'group_name',
            'department_name',
            'password',
            'is_superuser',
            'is_staff',
            'is_active'
        ]
        read_only_fields = ['last_login', 'date_joined']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        request = self.context['request']
        if 'password' in validated_data:
            validated_data.pop('password')
        if not (request.user.is_superuser or request.user.is_staff):
            validated_data['is_staff'] = instance.is_staff
            validated_data['is_superuser'] = instance.is_superuser
            validated_data['is_active'] = instance.is_active
        return super().update(instance, validated_data)


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    permissions_set = PermissionSerializer(source='permissions', read_only=True, many=True)
    permissions = serializers.ListField(write_only=True)

    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'desc',
            'detail',
            'email',
            'permissions',
            'permissions_set'
        ]


class ReadOnlyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username'
        ]


class ReadOnlyDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            'id',
            'name',
        ]


class GroupSerializer(serializers.ModelSerializer):
    department_set = DepartmentSerializer(source='departments', read_only=True, many=True)

    class Meta:
        model = Group
        fields = '__all__'
        read_only_fields = ['user_id']


class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = ['id', 'name', 'logo']

    def create(self, validated_data):
        SystemConfig.objects.all().delete()
        return super().create(validated_data)


class AliyunConfigSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = AliyunConfig
        fields = '__all__'


class SSHConfigSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = SSHConfig
        fields = '__all__'

    def validate_hostname(self, hostname):
        try:
            assert socket.gethostbyname(hostname) == hostname
        except Exception:
            raise serializers.ValidationError('Invalid hostname')
        return hostname

    def validate(self, attrs):
        attrs['password'] = encrypt(attrs['password'])
        return attrs
