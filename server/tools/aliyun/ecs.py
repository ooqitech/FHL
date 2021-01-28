import json

import math
from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest


class ECS:
    def __init__(self, key, secret, region):
        self.client = AcsClient(key, secret, region)

    def _instances(self, page_number=1):
        request = DescribeInstancesRequest()
        request.set_accept_format('json')
        request.set_Status("Running")
        request.set_PageNumber(page_number)
        request.set_PageSize(100)
        response = self.client.do_action_with_exception(request)
        return json.loads(str(response, encoding='utf-8'))

    def instances(self):
        """获取 ECS 所有实例信息"""
        total_page = math.ceil(self._instances()['TotalCount'] / 100)
        instances = {}
        for page_number in range(1, total_page + 1):
            for instance in self._instances(page_number)["Instances"]["Instance"]:
                vnc_ip = instance["VpcAttributes"]["PrivateIpAddress"]["IpAddress"]
                if vnc_ip:
                    inner_ip = vnc_ip[0]
                elif instance["InnerIpAddress"]["IpAddress"]:
                    inner_ip = instance["InnerIpAddress"]["IpAddress"][0]
                else:
                    inner_ip = ''

                if instance["PublicIpAddress"]["IpAddress"]:
                    public_ip = instance["PublicIpAddress"]["IpAddress"][0]
                else:
                    public_ip = ''
                instances[inner_ip] = {
                    'location': instance['ZoneId'],
                    'memory_size': instance['Memory'],
                    'cpu_count': instance['Cpu'],
                    'hostname': instance['InstanceName'],
                    'elastic_ip': instance['EipAddress']['IpAddress'],
                    'outer_ip_addr': public_ip,
                    'outer_bandwidth': instance["InternetMaxBandwidthOut"],
                }
        return instances
