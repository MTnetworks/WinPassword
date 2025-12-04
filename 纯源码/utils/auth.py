#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
认证模块 - 实现基于TOTP的Authenticator认证
"""

import os
import base64
import pyotp
import qrcode
from io import BytesIO
from PIL import Image
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet


class Authenticator:
    """Authenticator认证类，基于TOTP实现"""
    
    def __init__(self, config):
        self.config = config
        self.secret = None
        self.totp = None
        self.issuer = "密码管理工具"
    
    def setup(self, username):
        """设置新的Authenticator"""
        # 生成随机密钥
        self.secret = pyotp.random_base32()
        self.totp = pyotp.TOTP(self.secret)
        return self.secret
    
    def load(self, secret):
        """加载已有的Authenticator密钥"""
        self.secret = secret
        self.totp = pyotp.TOTP(self.secret)
    
    def verify(self, code):
        """验证TOTP代码"""
        if not self.totp:
            print("TOTP对象未初始化")
            return False
        
        # 获取当前代码进行比较
        current_code = self.totp.now()
        print(f"当前TOTP代码: {current_code}")
        print(f"用户输入的代码: {code}")
        print(f"验证结果: {current_code == code}")
        
        # 使用pyotp的verify方法进行验证（允许前后30秒的时间窗口）
        result = self.totp.verify(code)
        print(f"TOTP验证结果: {result}")
        return result
    
    def verify_totp(self, secret, code):
        """验证TOTP密钥和验证码"""
        try:
            # 创建临时TOTP对象
            temp_totp = pyotp.TOTP(secret)
            
            # 验证代码（允许前后30秒的时间窗口）
            result = temp_totp.verify(code)
            print(f"TOTP验证 - 密钥: {secret[:8]}..., 代码: {code}, 结果: {result}")
            return result
        except Exception as e:
            print(f"TOTP验证失败: {e}")
            return False
    
    def get_qr_code(self, username):
        """生成QR码图像"""
        if not self.secret:
            return None
        
        # 创建TOTP URI
        uri = pyotp.totp.TOTP(self.secret).provisioning_uri(
            name=username,
            issuer_name=self.issuer
        )
        
        # 生成QR码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        # 创建图像
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 转换为字节流
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
    
    def get_current_code(self):
        """获取当前TOTP代码（仅用于测试）"""
        if not self.totp:
            return None
        return self.totp.now()


class Encryption:
    """加密工具类，用于加密和解密数据"""
    
    @staticmethod
    def generate_key(master_password, salt=None):
        """从主密码生成加密密钥"""
        if salt is None:
            salt = os.urandom(16)
        
        # 使用PBKDF2派生密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        return key, salt
    
    @staticmethod
    def encrypt(data, key):
        """加密数据"""
        f = Fernet(key)
        return f.encrypt(data.encode())
    
    @staticmethod
    def decrypt(encrypted_data, key):
        """解密数据"""
        try:
            f = Fernet(key)
            return f.decrypt(encrypted_data).decode()
        except Exception as e:
            print(f"解密失败: {e}")
            return None

    def get_qr_code(self, username):
        """生成QR码图像"""
        if not self.secret:
            return None
        
        # 创建TOTP URI
        uri = pyotp.totp.TOTP(self.secret).provisioning_uri(
            name=username,
            issuer_name=self.issuer
        )
        
        # 生成QR码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        # 创建图像
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 转换为字节流
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()