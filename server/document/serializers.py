from rest_framework import serializers

from .models import Document, RsyncFiles


class DocumentSerializer(serializers.ModelSerializer):
    job_status = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    payload = serializers.JSONField(required=False)
    status = serializers.CharField(source='get_status_display', required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    plan_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    def _log(self, obj: Document):
        return obj.documentdistributelog_set.order_by('-id').first()

    def get_job_status(self, obj: Document):
        log = self._log(obj)
        return log and log.get_job_status_display() or '未执行'

    def get_message(self, obj: Document):
        log = self._log(obj)
        return log and log.message or ''

    class Meta:
        model = Document
        fields = '__all__'


class RsyncSerializer(serializers.ModelSerializer):
    job_status = serializers.ReadOnlyField(source='get_job_status_display')
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = RsyncFiles
        fields = '__all__'
