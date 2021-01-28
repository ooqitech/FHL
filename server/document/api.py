import base64
import json
import logging
import os
import subprocess
import tempfile
import time
from datetime import datetime

import requests
from celery import shared_task
from django.conf import settings

from cmdb.models import ECSInstance
from utils.ssh import default_sftp_client, default_ssh_client
from .models import Document, DocumentDistributeLog

logger = logging.getLogger('app')


class Client(object):
    """etcd client"""

    def __init__(self, host=settings.ETCD_HOST_URL, port=settings.ETCD_PORT):
        self.url = 'http://{}:{}'.format(host, port)
        self.key_url = self.url + '/v2/keys'

    def get(self, key, directory=None):
        """获取"""
        if directory:
            url = f'{self.key_url}/{directory}/{key}'
        else:
            url = f'{self.key_url}/{key}'
        try:
            resp = requests.get(url)
            return resp.json()
        except Exception as e:
            logger.error('获取配置失败：{}'.format(e))
            return {'code': 500, 'msg': '获取配置失败'}

    def put(self, key, value, directory=None):
        """新建或更新"""
        if directory:
            url = f'{self.key_url}/{directory}/{key}'
        else:
            url = f'{self.key_url}/{key}'
        try:
            resp = requests.put(url, data={'value': value})
            return resp.json()
        except Exception as e:
            logger.error('新建/更新配置失败: {}'.format(e))
            return {'code': 500, 'msg': '新建/更新配置失败'}

    def delete(self, key, directory=None):
        """删除对应键值对"""
        if directory:
            url = f'{self.key_url}/{directory}/{key}'
        else:
            url = f'{self.key_url}/{key}'
        try:
            resp = requests.delete(url)
            return resp.json
        except Exception as e:
            logger.error('删除配置失败: {}'.format(e))
            return {'code': 500, 'msg': '删除配置失败'}

    def create_dir(self, directory):
        try:
            resp = requests.put(f'{self.key_url}/{directory}',
                                data={'dir': 'true'})
            return resp.json
        except Exception as e:
            logger.error('创建目录失败：{}'.format(e))
            return {'code': 500, 'msg': '创建目录失败'}

    def delete_dir(self, directory):
        try:
            resp = requests.delete(f'{self.key_url}/{directory}?recursive=true')
            return resp.json()
        except Exception as e:
            logger.error('删除目录失败：{}'.format(e))
            return {'code': 500, 'msg': '删除目录失败'}


client = Client()

# 可上传文件
ETCD_FILE_TYPE = ["properties", "txt", "sql", "sh", "py", "xml", "yaml", "cfg", "ini", "config", "xmind", "data", "rmi",
                  "conf", "json", "toml"]

# 可分发文件
DISTRIBUTABLE_FILE = ["sql", "sh", "conf", "py", "properties", "xml", "yaml", "txt"]


def execute_recovery_command(hostname, remote_path, old_backup_path):
    """对某台服务器进行文件恢复"""
    try:
        with default_ssh_client(hostname=hostname) as ssh:
            backup_res = ssh.exec_command('cp "{}" "{}"'.format(old_backup_path, remote_path))
    except Exception:
        return {
            'status': False,
            'stderr': 'SSH 连接错误',
            'stdout': ''
        }
    if not backup_res['status'] and not backup_res['stderr'].strip().endswith('No such file or directory'):
        return backup_res
    else:
        return {
            'status': True,
            'stdout': '',
            'stderr': ''
        }


@shared_task
def restore_document(document_id):
    """
    恢复分发的配置
    Args:
        document_id: `.models.Document` 实例 ID
    """
    document = Document.objects.get(id=document_id)
    if not document.backup_path:
        logger.info('无备份')
        return None
    if DocumentDistributeLog.objects.filter(document_id=document.id, job_status=1).order_by('-id').first():
        return None
    log = DocumentDistributeLog.objects.create(document_id=document_id, job_status=1)
    try:
        payload = json.loads(document.payload) or {}
        servers = payload.get('servers') or []
        path = payload.get('path')
        logger.info('开始恢复备份【{}】'.format(document.name))
        remote_path = os.path.join(path, document.name).replace('\\', '/')
        for server_id in servers:
            server = ECSInstance.objects.filter(id=server_id).first()
            if not server:
                raise Exception('ID: {} 未找到主机'.format(server))
            else:
                server = server.inner_ip_addr
                res = execute_recovery_command(hostname=server, remote_path=remote_path,
                                               old_backup_path=document.backup_path)
                if not res['status']:
                    raise Exception('【{}】恢复失败：{}'.format(server, res.get('stderr')))

        log.job_status = 2
        log.message = '恢复备份成功'
        log.save()
        logger.info('配置恢复成功')
        document.backup_path = ''
        document.save()
        return True
    except Exception as e:
        msg = '【{} - {}】配置恢复失败 {}'.format(document.id, document.name, e)
        log.job_status = 3
        log.message = msg
        log.save()
        logger.error(msg)
        return False
    finally:
        log.end_time = datetime.now()
        log.save()


def distribute_file(hostname, remote_path, tmp_file, backup_path, other_commands=None):
    try:
        sftp = default_sftp_client(hostname=hostname)
    except Exception:
        return {
            'status': False,
            'stderr': 'SFTP 连接错误',
            'stdout': ''
        }
    try:
        ssh = default_ssh_client(hostname=hostname)
    except Exception:
        return {
            'status': False,
            'stderr': 'SSH 连接错误',
            'stdout': ''
        }
    # 备份服务器上的原有文件（如果有）
    backup_dir = os.path.dirname(backup_path)
    ssh.exec_command(f'mkdir {backup_dir} > /dev/null 2>&1')
    backup_res = ssh.exec_command(f'cp "{remote_path}" "{backup_path}"')
    if not backup_res['status']:
        if not backup_res['stderr'].strip().endswith('No such file or directory'):
            return backup_res

    if sftp.put_file(tmp_file, remotepath=remote_path):
        res = {
            'status': True,
            'stderr': None,
            'stdout': ''
        }
    else:
        return {
            'status': False,
            'stderr': f'文件推送失败，远程文件路径：{remote_path}',
            'stdout': ''
        }
    if other_commands and res.get('status'):
        for c in other_commands:
            res = ssh.exec_command(c)
            if not res.get('status'):
                return res
    return res


def parse_commands(cmd, path, name):
    commands = []

    if cmd:
        if 'owner' in cmd:
            commands.append('chown admin "{}"'.format(os.path.join(path, name).replace('\\', '/')))
        if 'group' in cmd:
            commands.append('chgrp admin "{}"'.format(os.path.join(path, name).replace('\\', '/')))

        if 'permission' in cmd:
            commands.append('chmod {} "{}"'.format(cmd['permission'], os.path.join(path, name).replace('\\', '/')))
    return commands


def distribute_document(document_id):
    """分发配置"""
    try:
        doc = Document.objects.filter(id=document_id).first()
        if not doc:
            return {
                'success': False,
                'message': '配置未找到'
            }

        log = DocumentDistributeLog.objects.create(document_id=doc.id, job_status=1)
        doc.status = 2
        doc.save()
        tmp_file = tempfile.NamedTemporaryFile('w+b')
        try:
            directory = '{}/{}'.format(doc.name.split('.')[-1], doc.md5)
            data = client.get(doc.name, directory=directory)
            if not data.get('node'):
                raise Exception('获取配置文件失败')

            content = base64.b64decode(data['node'].get('value').encode('utf-8'))

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
                    res = distribute_file(hostname=server, remote_path=remote_path, tmp_file=tmp_file.name,
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
            logger.info('配置分发成功')
            doc.backup_path = backup_path
            doc.save()
        except Exception as e:
            msg = '【{} - {}】执行异常 {}'.format(doc.id, doc.name, e)
            log.job_status = 3
            log.message = msg
            logger.error(msg)
        finally:
            tmp_file.close()
            log.end_time = datetime.now()
            log.save()
        return {
            'success': log.job_status == 2,
            'message': log.message,
        }
    except Exception as e:
        logger.error('系统异常：{}'.format(e))
        return {
            'success': False,
            'message': '系统异常'
        }


def rsync(src, dst):
    try:
        subprocess.run(['rsync', '-avz', src, dst], check=True)
    except subprocess.CalledProcessError as pe:
        logger.error(f'命令执行失败: {pe}')
        return False
    return True
