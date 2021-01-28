"""
SSH 执行远程命令与 SFTP 客户端
"""

import logging
import os
import socket
from pathlib import Path

import paramiko
from Crypto.PublicKey import RSA
from django.conf import settings

from .crypto import Crypto, decrypt

logger = logging.getLogger('app')


class SSHClient:
    """
    SSH 客户端
    """

    def __init__(self, hostname, port=22, username=None, password=None, **kwargs):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(hostname, port, username, password, **kwargs)
        except paramiko.AuthenticationException as auth_exp:
            logger.error(f'SSH 验证错误: {auth_exp}')
            raise auth_exp
        except socket.error as se:
            logger.error(f'socket 错误: {se}')
            raise se
        except paramiko.BadHostKeyException as bad_key_exp:
            logger.error(f'服务器 key 验证错误: {bad_key_exp}')
            raise bad_key_exp
        except paramiko.SSHException as ssh_exp:
            logger.error(f'SSH 连接错误: {ssh_exp}')
            raise ssh_exp

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.ssh:
            self.ssh.close()

    def exec_command(self, command, timeout=300, **kwargs):
        if not command:
            logger.error(f'无效命令: `{command}`')
            return {'status': False, 'stdout': '', 'stderr': '无效命令'}
        try:
            _, stdout, stderr = self.ssh.exec_command(command, timeout=timeout, **kwargs)
            stdout, stderr = stdout.read().decode('utf-8'), stderr.read().decode('utf-8')
            status = '失败' if stderr else '成功'
            logger.info(f'执行命令 `{command}` {status}')
        except paramiko.SSHException as ssh_exp:
            logger.error(f'执行命令 `{command}` 失败: {ssh_exp}')
            stdout, stderr = '', str(ssh_exp)
        return {
            'status': False if stderr else True,
            'stdout': stdout,
            'stderr': stderr
        }

    def close(self):
        self.ssh.close()


class SFTPClient:
    """SFTP 客户端"""

    def __init__(self, username, password, hostname, port=22, **kwargs):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname, port, username, password, **kwargs)

        self.sftp = paramiko.SFTPClient.from_transport(self.ssh.get_transport())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.sftp:
            self.sftp.close()
        if self.ssh:
            self.ssh.close()

    def get_pwd(self):
        return self.sftp.getcwd()

    def put_file(self, localpath: str, remotepath: str):
        """
        上传文件到服务器
        Args:
            localpath: 本地路径
            remotepath: 远程路径

        Returns:
            bool: 成功返回 True

        """

        if str(remotepath).strip().endswith('/'):
            remotepath = remotepath + os.path.basename(localpath)
        try:
            self.sftp.put(localpath=localpath, remotepath=remotepath)
            return True
        except IOError:
            return False

    def get_file(self, localpath: str, remotepath: str):
        """
        下载远程文件
        Args:
            remotepath: 远程路径
            localpath: 本地路径

        Returns:
            bool: 成功返回 True

        """

        try:
            self.sftp.get(remotepath=remotepath, localpath=localpath)
            return True
        except IOError:
            return False

    def rsync(self, remotepath: Path, localpath: Path):
        """"""


def default_ssh_client(key=None, hostname=None):
    """"""
    if key:
        _decrypt = Crypto(key=key).decrypt
    else:
        _decrypt = decrypt
    password = _decrypt(settings.SSH_PASSWORD)
    client = SSHClient(hostname=hostname, username=settings.SSH_USER, password=password)
    return client


def default_sftp_client(key=None, hostname=None):
    """"""
    if key:
        _decrypt = Crypto(key=key).decrypt
    else:
        _decrypt = decrypt
    password = _decrypt(settings.SSH_PASSWORD)
    client = SFTPClient(hostname=hostname, username=settings.SSH_USER, password=password)
    return client


def gen_rsa_key():
    """幂等"""
    path = Path(os.path.expanduser('~'))
    ssh_path = path / '.ssh'
    if not ssh_path.exists():
        ssh_path.mkdir(0o700)
    key_path = ssh_path / 'id_rsa'
    pub_path = ssh_path / 'id_rsa.pub'
    if not key_path.exists() or not pub_path.exists():
        key = RSA.generate(2048)
        with key_path.open('wb') as file:
            os.chmod(str(key_path), 0o600)
            file.write(key.export_key('PEM'))
        pubkey = key.publickey()
        with open(str(pub_path), 'wb') as file:
            file.write(pubkey.export_key('OpenSSH'))
        logger.info('Create ~/.ssh/id_rsa and ~/.ssh/id_rsa.pub')
        return pubkey.export_key('OpenSSH')
    with pub_path.open('rb') as file:
        return file.read()


def send_pub_key(username, password, hostname):
    """幂等"""

    def write_key():
        f = client.sftp.open('.ssh/authorized_keys', 'wb')
        f.write(b'\n'.join(keys))
        f.chmod(0o600)
        f.close()

    try:
        with SFTPClient(hostname=hostname, username=username, password=password) as client:
            try:
                client.sftp.stat('.ssh/')
            except FileNotFoundError:
                client.sftp.mkdir('.ssh/', mode=0o700)
            key = gen_rsa_key().strip()
            try:
                client.sftp.stat('.ssh/authorized_keys')
            except FileNotFoundError:
                keys = [key]
                write_key()
                logger.info('Create new authorized_keys and write public key')
            else:
                file = client.sftp.open('.ssh/authorized_keys', 'rb')
                keys = [line.strip() for line in file.readlines()]
                if key not in keys:
                    keys.append(key)
                    file.close()
                    write_key()
                    logger.info('Write new public key')
        return True

    except IOError as e:
        logger.error(f'发送公钥到服务器失败: {e}')
        return False
