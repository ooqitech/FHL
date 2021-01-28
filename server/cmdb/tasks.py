import json
import logging

from celery import shared_task

from account.models import AliyunConfig
from tools.aliyun import ECS, RDS, SLB
from .models import ECSInstance, LoadBalancers, RDSDatabase, RDSInstance, SLBBackendServers

logger = logging.getLogger('app')


@shared_task
def periodic_sync_slb():
    """定时同步 SLB 信息"""
    logger.info('开始同步 SLB')
    for config in AliyunConfig.objects.all():
        try:
            slb_info = SLB(config.key, config.secret, config.region).load_balancers()
        except Exception as e:
            logger.error(f'获取 SLB 信息失败: {e}-{config.key}')
            continue
        old_slb_ids = [lb.slb_id for lb in LoadBalancers.objects.all()]
        slb_ids = slb_info.keys()

        for delete_slb in set(old_slb_ids) - set(slb_ids):
            # 删除下线的 Load balancer
            SLBBackendServers.objects.filter(lb_id=delete_slb).delete()
            LoadBalancers.objects.filter(slb_id=delete_slb).delete()
            logger.info(f'删除下线的 Load balancer: {delete_slb}')

        current_servers = set()
        old_backend_servers = set()
        for server in SLBBackendServers.objects.all():
            old_backend_servers.add(f'{server.ip_addr}/{server.port}')

        for slb_id, info in slb_info.items():
            servers = info.pop('servers')
            info['ports'] = json.dumps(info['ports'])
            load_balancer = LoadBalancers.objects.filter(slb_id=slb_id).first()
            if not load_balancer:
                # 新增 Load balancer
                LoadBalancers.objects.create(slb_id=slb_id, **info)
            else:
                # 更新 Load balancer 端口
                if info['ports'] != load_balancer.ports:
                    load_balancer.ports = info['ports']
                    load_balancer.save()
            for server in servers:
                server['lb_id'] = slb_id
                # 新增 Backend Server
                if not SLBBackendServers.objects.filter(**server).first():
                    SLBBackendServers.objects.create(**server)
                    logger.info(f'新增 Backend Server: {server}')
                current_servers.add(f'{server["ip_addr"]}/{server["port"]}')
        # 删除下线的 Backend Server
        for server in old_backend_servers - current_servers:
            ip_addr, port = server.split('/')
            SLBBackendServers.objects.filter(ip_addr=ip_addr, port=port).delete()
            logger.info(f'删除下线的 Backend Server: {server}')

    logger.info('同步 SLB 完成')


@shared_task
def periodic_sync_rds():
    """定时同步 RDS 信息"""
    logger.info('开始同步 RDS')
    for config in AliyunConfig.objects.all():
        try:
            rds_info = RDS(config.key, config.secret, config.region).db_instances()
        except Exception as e:
            logger.error(f'获取 RDS 信息失败: {e}')
            return False
        i_count, d_count = 0, 0
        all_databases = []
        for instance_id, info in rds_info.items():
            db_instance = RDSInstance.objects.filter(name=instance_id).all().first()
            databases = info.pop('databases')
            if not db_instance:
                logger.info(f'新增 RDS 实例一个: {instance_id}: {info}')
                i_count += 1
                db_instance = RDSInstance.objects.create(name=instance_id, **info)
            for database in databases:
                all_databases.append(f'{instance_id}|||{database["db_name"]}')
                if not RDSDatabase.objects.filter(db_name=database['db_name'], db_instance_id=db_instance.id).first():
                    logger.info(f'{db_instance.name} 新增数据库: {database}')
                    RDSDatabase.objects.create(db_instance_id=db_instance.id, **database)
                    d_count += 1

        for db_instance in RDSInstance.objects.all():
            if db_instance.name not in rds_info:
                logger.info(f'删除下线数据库实例: {db_instance.name}')
                RDSDatabase.objects.filter(db_instance=db_instance).delete()
                db_instance.delete()

        for database in RDSDatabase.objects.all():
            if f'{database.db_instance.name}|||{database.db_name}' not in all_databases:
                logger.info(f'删除下线数据库 {database.db_instance.name}/{database.db_name}')
                database.delete()

        logger.info(f'同步 RDS 完成，新增实例 {i_count} 个，新增数据库 {d_count} 个')


@shared_task
def periodic_sync_ecs():
    """定时同步 ECS 信息"""
    logger.info('开始同步 ECS')
    for config in AliyunConfig.objects.all():
        try:
            ecs_info = ECS(config.key, config.secret, config.region).instances()
        except Exception as e:
            logger.error(f'获取 ECS 信息失败: {e}')
            return False
        update_fields = ['hostname', 'outer_ip_addr', 'elastic_ip', 'cpu_count', 'memory_size']
        new_count, update_count = 0, 0
        for ip, info in ecs_info.items():
            ecs = ECSInstance.objects.filter(inner_ip_addr=ip).values().first()
            if not ecs:
                ECSInstance.objects.create(inner_ip_addr=ip, **info)
                new_count += 1
                logger.info(f'新建 ECS 实例: {ip}: {info}')
            else:
                for field in update_fields:
                    if ecs.get(field) != info.get(field):
                        logger.info(f'更新 ECS 实例: {ip}: {info}')
                        ECSInstance.objects.filter(inner_ip_addr=ip).update(**info)
                        update_count += 1
                        break

        logger.info(f'同步 ECS 完成，新建 ECS {new_count} 个，更新 {update_count} 个')
