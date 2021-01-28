import json
import logging
import os
import tempfile
import time
from datetime import datetime

from celery import shared_task
from django.conf import settings

from cmdb.models import ECSInstance
from utils.ssh import send_pub_key
from .api import client, distribute_file, execute_recovery_command, parse_commands, rsync
from .models import Document, DocumentDistributeLog, RsyncFiles

logger = logging.getLogger('app')


@shared_task
def auto_distribute_config():
    """自动分发配置"""
    try:
        docs = Document.objects.filter(status=1).all()
        for doc in docs:
            if datetime.now() <= doc.plan_time:
                continue
            log = DocumentDistributeLog.objects.create(document_id=doc.id, job_status=1)
            doc.status = 2
            doc.save()
            tmp_file = tempfile.TemporaryFile('w+b')
            try:
                directory = '{}/{}'.format(doc.name.split('.')[-1], doc.md5)
                data = client.get(doc.name, directory=directory)
                if not data.get('node'):
                    raise Exception('获取配置文件失败')

                content = data['node'].get('value')

                payload = json.loads(doc.payload) or {}
                servers = payload.get('servers') or []
                path = payload.get('path')
                commands = parse_commands(payload.get('commands') or {}, path=path, name=doc.name)
                remote_path = os.path.join(path, doc.name).replace('\\', '/')
                backup_path = os.path.join(path, settings.ETCD_AUTO_BACKUP_DIR,
                                           '{}-{}'.format(int(time.time() * 1000), doc.name)).replace('\\', '/')
                tmp_file.write(content)
                success = []
                logger.info(f'开始分发配置【{doc.name}】')
                for server_id in servers:
                    server = ECSInstance.objects.filter(id=server_id).first()
                    if not server:
                        logger.error(f'ID 为 {server_id} 的主机未找到，任务失败，开始回滚成功分发的机器: {success}')
                        for success_server in success:
                            res = execute_recovery_command(hostname=success_server, remote_path=remote_path,
                                                           old_backup_path=backup_path)
                            if not res["status"]:
                                logger.error('机器[{}]回滚失败：{}'.format(success_server, res['stderr']))
                        raise Exception('ID: {} 未找到主机'.format(server))
                    else:
                        server = server.inner_ip_addr
                        res = distribute_file(hostname=server, remote_path=remote_path, tmp_file=tmp_file,
                                              backup_path=backup_path, other_commands=commands)
                        if not res['status']:
                            logger.info('任务失败，开始回滚成功分发的机器: {}'.format(success))
                            for success_server in success:
                                _res = execute_recovery_command(hostname=success_server, remote_path=remote_path,
                                                                old_backup_path=backup_path)
                                if not _res["status"]:
                                    logger.error('机器[{}]回滚失败：{}'.format(success_server, _res['stderr']))
                            raise Exception('【{}】执行远程命令失败：{}'.format(server, res.get('stderr')))
                        success.append(server)
                log.job_status = 2
                log.save()
                logger.info('配置分发成功')
                doc.backup_path = backup_path
                doc.save()
            except Exception as e:
                msg = '【{} - {}】执行失败 {}'.format(doc.id, doc.name, e)
                log.job_status = 3
                log.message = msg
                log.save()
                logger.error(msg)
            finally:
                tmp_file.close()
                log.end_time = datetime.now()
                log.save()
    except Exception as e:
        logger.error('系统异常：{}'.format(e))


@shared_task
def periodic_rsync_files():
    """实时同步文件"""
    for sync in RsyncFiles.objects.all():
        logger.info(f'开始同步 {sync.src} 到 {sync.dst}')
        try:
            send_pub_key(username=sync.ssh.username, password=sync.ssh.raw_password,
                         hostname=sync.ssh.hostname)
            if not rsync(sync.src, sync.dst):
                logger.error('同步文件失败')
                sync.job_status = 3
            else:
                sync.job_status = 2
                logger.info('同步成功')
        except Exception as e:
            sync.job_status = 3
            logger.error(f'同步异常: {e}')
