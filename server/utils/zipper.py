"""
文件压缩/解压(zip 格式)
"""
import logging
import os
import pathlib
import shutil
import zipfile

logger = logging.getLogger('app')


def compress(src: str, dst: str):
    """
    压缩文件
    Args:
        src: 源目录/文件
        dst: 目标文件

    Examples:
    >>> compress('/root/this_is_a_dir', '/home/user/out_file')
    '/home/user/out_file.zip'
    >>> compress('/root/this_is_a_dir', '')
    "$(pwd).zip"
    >>> compress('/root/file.txt', 'abc')
    "$(pwd)/abc.zip"
    """

    src = os.path.abspath(src)
    dst = os.path.abspath(dst)
    src_path = pathlib.Path(src)
    if not src_path.exists():
        logger.error(f'压缩路径 {src} 不存在')
        return False
    root_dir, base_dir = src_path.parent, src_path.name
    if dst.endswith('.zip'):
        dst = dst[:-4]
    try:
        return shutil.make_archive(base_name=dst, format='zip', root_dir=root_dir, base_dir=base_dir)
    except OSError as os_error:
        logger.error(f'添加压缩文件({dst}.zip)失败：{os_error}')


def unzip(zip_file, target_path: str):
    """
    解压 zip 文件
    Args:
        zip_file: 压缩文件
        target_path: 输出路径

    Examples:
    >>> unzip('./abc.zip', '')
    "$(pwd)"
    >>> unzip('./abc.zip', '/root/foo/bar')
    "/root/foo/bar"
    >>> unzip('./not_a_zip_file.zip', '/root/foo/bar')
    False
    """

    if not zipfile.is_zipfile(zip_file):
        logger.error(f'{zip_file} 不是有效的 zip 压缩文件')
        return False
    try:
        if not target_path:
            target_path = os.getcwd()
        with zipfile.ZipFile(zip_file) as zf:
            zf.extractall(target_path)
        return target_path
    except FileNotFoundError:
        logger.error(f'解压存放路径({target_path})不存在')
        return False
    except OSError as os_error:
        logger.error(f'解压路径无效: {os_error}')
        return False
