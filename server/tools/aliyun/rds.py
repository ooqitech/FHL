import json
import logging

import math
from aliyunsdkcore.client import AcsClient
from aliyunsdkrds.request.v20140815.DescribeDBInstanceNetInfoRequest import DescribeDBInstanceNetInfoRequest
from aliyunsdkrds.request.v20140815.DescribeDBInstancesRequest import DescribeDBInstancesRequest
from aliyunsdkrds.request.v20140815.DescribeDatabasesRequest import DescribeDatabasesRequest

logger = logging.getLogger('app')


class RDS:
    def __init__(self, key, secret, region):
        self.client = AcsClient(key, secret, region)

    def _db_instances(self, page_number=1):
        """完整实例信息"""
        request = DescribeDBInstancesRequest()
        request.set_accept_format('json')
        request.set_DBInstanceStatus("Running")
        request.set_PageNumber(page_number)
        request.set_PageSize(100)
        response = self.client.do_action_with_exception(request)
        return json.loads(str(response, encoding='utf-8'))

    def _net_info(self, instance_id, ip_type='Private'):
        request = DescribeDBInstanceNetInfoRequest()
        request.set_accept_format('json')
        request.set_DBInstanceId(instance_id)
        response = self.client.do_action_with_exception(request)
        data = json.loads(str(response, encoding='utf-8'))
        if ip_type:
            info = []
            for d in data['DBInstanceNetInfos']['DBInstanceNetInfo']:
                if d['IPType'] == ip_type:
                    info.append(d)
            return info
        return data['DBInstanceNetInfos']['DBInstanceNetInfo']

    def db_connection(self, instance_id):
        """数据库连接地址"""
        return self._net_info(instance_id)[0]['ConnectionString']

    def db_instances(self):
        """获取数据库实例相关信息"""
        instances = {}
        total_page = math.ceil(self._db_instances()['TotalRecordCount'] / 100)
        for page_number in range(1, total_page + 1):
            for instance in self._db_instances(page_number)["Items"]["DBInstance"]:
                instance_id = instance["DBInstanceId"]
                instances[instance_id] = {
                    'db_description': instance["DBInstanceDescription"],
                    'db_engine': instance["Engine"],
                    'db_connection': self.db_connection(instance_id),
                    'is_online': 1,
                    'databases': self.databases(instance_id),
                }
        return instances

    def _databases(self, instance_id):
        """根据实例获取数据库信息"""
        request = DescribeDatabasesRequest()
        request.set_accept_format('json')
        request.set_DBInstanceId(instance_id)
        response = self.client.do_action_with_exception(request)
        return json.loads(str(response, encoding='utf-8'))['Databases']['Database']

    def databases(self, instance_id):
        """根据实例获取经过处理的数据库信息"""
        databases = self._databases(instance_id)
        info = []
        for database in databases:
            info.append({
                'is_online': database['DBStatus'] == 'Running',
                'db_name': database['DBName'],
                'db_engine': database['Engine'],
                # 'desc': database['DBDescription'],
            })
        return info
