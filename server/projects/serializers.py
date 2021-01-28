import os

from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    app_status = serializers.ReadOnlyField(source='get_status_display')
    app_type = serializers.ReadOnlyField(source='get_project_type_display')
    promoted_number = serializers.SerializerMethodField()
    department = serializers.ReadOnlyField(source='department.name')
    dev = serializers.ReadOnlyField(source='dev_group.name')
    test = serializers.ReadOnlyField(source='test_group.name')
    department_id = serializers.IntegerField(write_only=True)
    dev_group_id = serializers.IntegerField(write_only=True)
    test_group_id = serializers.IntegerField(write_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = Project
        read_only_fields = ['is_health']
        exclude = ['status', 'dev_group', 'test_group']

    def get_promoted_number(self, obj: Project):
        """生产构建号"""
        try:
            if obj.productionapp:
                return obj.productionapp.version.promoted_number
        except Exception:
            return None
        return None

    def validate(self, attrs):
        if attrs['project_type'] == 3:
            if not attrs['name'].lower().startswith('h5-'):
                raise serializers.ValidationError({'name': 'H5 项目必须以 h5- 开头'})
            if not attrs['app_dir'] or not os.path.exists(attrs['app_dir']):
                raise serializers.ValidationError({'app_dir': 'H5 应用路径无效'})

        return attrs

    def update(self, instance, validated_data):
        validated_data.pop('name', None)  # 项目名不能更新
        validated_data.pop('is_root', None)
        validated_data.pop('project_type', None)
        return super().update(instance, validated_data)


class SimpleProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'chinese_name', 'project_type']
