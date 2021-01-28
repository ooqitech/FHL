import json
import logging
import re

import math
from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkslb.request.v20140515.DescribeHealthStatusRequest import DescribeHealthStatusRequest
from aliyunsdkslb.request.v20140515.DescribeLoadBalancerAttributeRequest import DescribeLoadBalancerAttributeRequest
from aliyunsdkslb.request.v20140515.DescribeLoadBalancersRequest import DescribeLoadBalancersRequest

logger = logging.getLogger('app')


class SLB:
    def __init__(self, key, secret, region):
        self.client = AcsClient(key, secret, region)
        self.rex = re.compile(r'192.168.\d{3}.\d')

    def _attribute(self, lb_id):
        """
        查询指定负载均衡实例的详细信息
        Args:
            lb_id: 负载均衡实例 ID

        Returns:

        """
        request = DescribeLoadBalancerAttributeRequest()
        request.set_accept_format('json')
        request.set_LoadBalancerId(lb_id)
        response = self.client.do_action_with_exception(request)
        return json.loads(str(response, encoding='utf-8'))

    def _ports(self, lb_id) -> list:
        attribute = self._attribute(lb_id)
        return attribute["ListenerPorts"]["ListenerPort"]

    def _health_status(self, lb_id):
        """
        查询后端服务器的健康状态
        Args:
            lb_id: 负载均衡实例 ID

        Returns:

        """
        request = DescribeHealthStatusRequest()
        request.set_accept_format('json')
        request.set_LoadBalancerId(lb_id)
        response = self.client.do_action_with_exception(request)
        return json.loads(str(response, encoding='utf-8'))["BackendServers"]["BackendServer"]

    def _ecs_instances(self, instance_ids):
        """
        根据实例 ID 查询一台或多台ECS实例的详细信息
        Args:
            instance_ids: ECS 实例 ID 列表

        Returns:

        """
        if isinstance(instance_ids, str):
            instance_ids = [instance_ids]
        request = DescribeInstancesRequest()
        request.set_accept_format('json')
        request.set_InstanceIds(instance_ids)
        response = self.client.do_action_with_exception(request)
        return json.loads(str(response, encoding='utf-8'))["Instances"]["Instance"]

    def _servers(self, lb_id):
        _servers = self._health_status(lb_id)
        servers = []
        for server in _servers:
            ecs = self._ecs_instances(server['ServerId'])[0]
            ip = ecs["VpcAttributes"]["PrivateIpAddress"]["IpAddress"]
            ip = ip[0] if ip else ''
            servers.append({
                'ip_addr': ip,
                'port': server['Port'],
            })
        return servers

    def _load_balancers(self, page_number=1):
        """获取负载均衡实例"""
        request = DescribeLoadBalancersRequest()
        request.set_accept_format('json')
        request.set_LoadBalancerStatus("active")
        request.set_PageNumber(page_number)
        request.set_PageSize(100)
        response = self.client.do_action_with_exception(request)
        return json.loads(str(response, encoding='utf-8'))

    def load_balancers(self):
        total_page = math.ceil(self._load_balancers()['TotalCount'] / 100)
        instances = {}
        for page in range(1, total_page + 1):
            for lb in self._load_balancers(page)["LoadBalancers"]["LoadBalancer"]:
                if lb["AddressType"] == "intranet" and self.rex.match(lb["Address"]):
                    lb_id = lb['LoadBalancerId']
                    instances[lb_id] = {
                        'ip_addr': lb['Address'],
                        'ports': self._ports(lb_id),
                        'servers': self._servers(lb_id),  # 后端服务器
                    }

        return instances
