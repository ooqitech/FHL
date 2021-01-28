"""
加密解密模块
"""
import base64
import hashlib

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from django.conf import settings


class Crypto:
    def __init__(self, key=settings.CRYPTO_KEY, mode=AES.MODE_CBC, block_size=16):
        self.key = pad(key, block_size)
        self.iv = self.key[:16]
        self.mode = mode
        self.block_size = block_size

    def encrypt(self, plaintext):
        """

        Args:
            plaintext: 要加密的文本

        Returns:
            base64 编码后的文本

        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        plaintext = pad(plaintext, self.block_size)
        cipher = AES.new(self.key, self.mode, self.iv)
        encrypt_aes = cipher.encrypt(plaintext)
        encrypted = base64.urlsafe_b64encode(encrypt_aes)
        return encrypted.decode('utf-8')

    def decrypt(self, cipher_text):
        cipher = AES.new(self.key, self.mode, self.iv)
        cipher_bytes = base64.urlsafe_b64decode(cipher_text.encode('utf-8'))
        decrypted = cipher.decrypt(cipher_bytes)
        decrypted = unpad(decrypted, self.block_size)
        return decrypted.decode('utf-8')


cryptor = Crypto()

encrypt = cryptor.encrypt
decrypt = cryptor.decrypt


def md5_calc(file):
    md5_value = hashlib.md5()
    with open(file, 'rb') as file_b:
        while True:
            data_flow = file_b.read(8096)
            if not data_flow:
                break
            md5_value.update(data_flow)
    file_b.close()
    return md5_value.hexdigest()
