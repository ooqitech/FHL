from rest_framework import serializers

from .models import ECSInstance, RDSDatabase, Staff


class DatabaseSerializer(serializers.ModelSerializer):
    db_engine_name = serializers.ReadOnlyField(source='db_instance.app_name')
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = RDSDatabase
        fields = '__all__'


class SimpleDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RDSDatabase
        fields = ['id', 'db_name']


class EcsSerializer(serializers.ModelSerializer):
    app_name = serializers.ReadOnlyField(source='app.name')
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ECSInstance
        fields = ['id', 'app_id', 'app_name', 'inner_ip_addr', 'outer_ip_addr', 'elastic_ip', 'hostname', 'cpu_count',
                  'memory_size', 'disk_size', 'update_time']

        read_only_fields = ['inner_ip_addr', 'outer_ip_addr', 'elastic_ip', 'hostname', 'cpu_count',
                            'memory_size', 'disk_size', 'update_time']


class SimpleEcsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ECSInstance
        fields = ['id', 'inner_ip_addr', 'hostname']


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'
