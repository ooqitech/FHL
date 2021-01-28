"""
包装好的 FTP 客户端
"""
import logging
import re
from ftplib import FTP
from io import BytesIO
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('app')

pattern = re.compile(f'ftp://(.*?):(.*?)@(.*?)/(.*$)')


class FTPClient(FTP):
    def __init__(self, host=settings.FTP_HOST, user=settings.FTP_USER, passwd=settings.FTP_PASSWORD,
                 encoding='utf-8', **kwargs):
        super().__init__(host=host, user=user, passwd=passwd, **kwargs)
        self.encoding = encoding

    def download(self, remote_path, local_path):
        """
        下载文件
        Args:
            remote_path: 远程路径
            local_path: 本地路径

        Returns:

        """
        path = Path(local_path).parent
        try:
            if not path.exists():
                path.mkdir()
            with open(local_path, 'wb') as f:
                self.retrbinary(f'RETR {remote_path}', f.write)
            return True
        except OSError as error:
            logger.error(f'下载文件({remote_path})失败: {error}')
            return False

    def upload(self, remote_path, local_path, dirname=None):
        """
        上传文件
        Args:
            remote_path: 远程路径
            local_path: 本地路径
            dirname: 需要创建的远程目录
        """
        try:
            if dirname:
                self.mkd(dirname)
            with open(local_path, 'rb') as f:
                self.storbinary(f'STOR {remote_path}', f)
            return True
        except OSError as error:
            logger.error(f'上传文件({local_path} to {remote_path})失败: {error}')
            return False


def read_ftp(host, user, password, file_path, encoding='utf-8-sig'):
    """
    读取 ftp 远程文件，并以给定 encoding 转为字符，指定为 None 时返回字节
    Args:
        host: 远程地址
        user: FTP 用户
        password: FTP 密码
        file_path: 远程路径
        encoding: 文件编码

    Returns:
        str/bytes: 使用 encoding 解码远程文件的内容，encoding 为 None 时返回原始字节

    """
    with FTPClient(host=host, user=user, passwd=password) as ftp:
        r = BytesIO()
        ftp.retrbinary(f'RETR {file_path}', r.write)
        if encoding:
            return r.getvalue().decode(encoding)
        else:
            return r.getvalue()


def read_ftp_url(ftp_url, encoding='utf-8-sig') -> str:
    """
    从 FTP url 中解析主机、用户名、密码并读取文件
    Args:
        ftp_url: 包含主机、用户名、密码的 FTP url
        encoding: FTP 远程文件编码

    Returns:
        str: FTP 文件内容
    """
    if not encoding:
        encoding = 'utf-8-sig'

    ftp_url = ftp_url.replace('\\', '/')
    user, password, url, path = pattern.match(ftp_url).groups()
    try:
        return read_ftp(user=user, password=password, host=url, file_path=path, encoding=encoding)
    except UnicodeDecodeError:
        return read_ftp(user=user, password=password, host=url, file_path=path, encoding='gbk')


def default_ftp_client():
    return FTPClient()
