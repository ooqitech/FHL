"""
获取本机 IP 地址
"""
import socket


def get_host_ip():
    """Get localhost ip addr

    Returns:
        str -- ip addr
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip
