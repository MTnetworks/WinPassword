#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
密码数据库模块
"""

import os
import json
import time
import shutil
from datetime import datetime
from utils.auth import Encryption


class PasswordDatabase:
    """密码数据库类，负责管理密码数据"""
    
    def __init__(self, config):
        self.config = config
        self.db_path = None
        self.key = None
        self.salt = None
        self.data = {
            "categories": [],
            "passwords": [],
            "last_modified": None,
            "version": "1.0",
            "totp_secret": None,  # 存储TOTP密钥
            "username": ""  # 存储用户名
        }
        self.default_categories = [
            "网站", "应用", "邮箱", "银行", "证件", "其他"
        ]
        
        # 错误处理属性
        self.last_error = None
        self.last_error_message = None
        
        # 初始化云同步管理器
        from utils.cloud_sync import CloudSyncManager
        self.cloud_sync = CloudSyncManager(config)
    
    def create(self, db_path, master_password, totp_secret=None, username=""):
        """创建新的密码数据库"""
        print(f"数据库创建：用户指定路径: {db_path}")
        
        # 如果启用了云存储，需要特殊处理
        if self.config.get_cloud_config("enabled"):
            # 临时保存用户路径到配置以获取有效路径
            original_db_path = self.config.get("database_path")
            self.config.set("database_path", db_path)
            effective_path = self.config.get_effective_database_path()
            print(f"数据库创建：云存储启用，有效路径: {effective_path}")
            
            # 如果有效路径与用户选择路径不同，说明使用了云存储
            if effective_path != db_path:
                # 先在用户选择的路径创建数据库
                self.db_path = db_path
                print(f"数据库创建：先在本地路径创建: {db_path}")
            else:
                self.db_path = effective_path
        else:
            self.db_path = db_path
        
        # 生成加密密钥
        self.key, self.salt = Encryption.generate_key(master_password)
        
        # 初始化数据
        self.data = {
            "categories": self.default_categories,
            "passwords": [],
            "last_modified": datetime.now().isoformat(),
            "version": "1.0",
            "totp_secret": totp_secret,  # 存储TOTP密钥
            "username": username  # 存储用户名
        }
        
        # 保存数据库
        if not self.save():
            return False
        
        # 如果启用了云存储且路径不同，将数据库文件复制到云存储路径
        if self.config.get_cloud_config("enabled"):
            # 重新获取有效路径
            self.config.set("database_path", db_path)
            effective_path = self.config.get_effective_database_path()
            if effective_path != self.db_path and os.path.exists(self.db_path):
                try:
                    # 确保云存储目录存在
                    os.makedirs(os.path.dirname(effective_path), exist_ok=True)
                    # 复制到云存储路径
                    import shutil
                    shutil.copy2(self.db_path, effective_path)
                    print(f"数据库创建：已复制到云存储路径: {effective_path}")
                    # 更新数据库路径为云存储路径
                    self.db_path = effective_path
                    # 更新配置中的路径为实际的云存储路径
                    self.config.set("database_path", effective_path)
                    print(f"数据库创建：更新配置路径为: {effective_path}")
                except Exception as e:
                    print(f"复制到云存储失败: {e}")
                    # 复制失败时保持使用本地路径，并保存本地路径到配置
                    self.config.set("database_path", self.db_path)
            else:
                # 保存最终的数据库路径到配置
                self.config.set("database_path", self.db_path)
        else:
            # 非云存储模式，直接保存用户路径到配置
            self.config.set("database_path", db_path)
        
        print(f"数据库创建：最终保存到配置的路径: {self.config.get('database_path')}")
        return True
    
    def open(self, db_path, master_password):
        """打开现有的密码数据库"""
        # 清除之前的错误状态
        self.last_error = None
        self.last_error_message = None
        
        # 如果启用了云存储，先尝试从远程同步
        if self.cloud_sync.is_cloud_enabled():
            cloud_db_path = self.config.get_effective_database_path()
            
            # 如果配置了打开时同步，先从远程同步
            if self.config.get_cloud_config("sync_on_open"):
                self.cloud_sync.sync_from_remote(cloud_db_path)
            
            # 检查云存储路径的文件是否存在
            if os.path.exists(cloud_db_path):
                self.db_path = cloud_db_path
            else:
                # 云存储文件不存在，回退到本地路径
                print(f"云存储数据库文件不存在: {cloud_db_path}，尝试使用本地路径: {db_path}")
                if os.path.exists(db_path):
                    self.db_path = db_path
                    print(f"找到本地数据库文件: {db_path}")
                else:
                    self.last_error = "FILE_NOT_FOUND"
                    self.last_error_message = f"数据库文件不存在，云存储路径: {cloud_db_path}，本地路径: {db_path}"
                    print(f"打开数据库失败: {self.last_error_message}")
                    return False
        else:
            self.db_path = db_path
        
        try:
            # 再次检查最终确定的文件路径是否存在
            if not os.path.exists(self.db_path):
                self.last_error = "FILE_NOT_FOUND"
                self.last_error_message = f"数据库文件不存在: {self.db_path}"
                print(f"打开数据库失败: {self.last_error_message}")
                return False
            
            # 读取加密的数据库文件
            with open(self.db_path, "rb") as f:
                encrypted_data = f.read()
            
            # 检查文件是否为空或太小
            if len(encrypted_data) < 16:
                self.last_error = "DATA_CORRUPTED"
                self.last_error_message = "数据库文件损坏或格式不正确"
                print(f"打开数据库失败: {self.last_error_message}")
                return False
            
            # 读取盐值（存储在文件开头）
            salt = encrypted_data[:16]
            encrypted_content = encrypted_data[16:]
            
            # 生成密钥
            self.key, self.salt = Encryption.generate_key(master_password, salt)
            
            # 解密数据
            decrypted_data = Encryption.decrypt(encrypted_content, self.key)
            if not decrypted_data:
                self.last_error = "INVALID_KEY"
                self.last_error_message = "TOTP密钥错误，无法解密数据库"
                print(f"打开数据库失败: {self.last_error_message}")
                return False
            
            # 解析JSON数据
            try:
                self.data = json.loads(decrypted_data)
            except json.JSONDecodeError as e:
                self.last_error = "DATA_CORRUPTED"
                self.last_error_message = f"数据库文件损坏，JSON解析失败: {str(e)}"
                print(f"打开数据库失败: {self.last_error_message}")
                return False
            
            # 验证TOTP密钥是否匹配数据库中存储的密钥
            if "totp_secret" in self.data and self.data["totp_secret"]:
                input_key = str(master_password).strip()
                stored_key = str(self.data["totp_secret"]).strip()
                print(f"调试信息 - 输入的TOTP密钥: '{input_key}' (长度: {len(input_key)})")
                print(f"调试信息 - 存储的TOTP密钥: '{stored_key}' (长度: {len(stored_key)})")
                print(f"调试信息 - 密钥比较结果: {input_key == stored_key}")
                
                if input_key != stored_key:
                    # TOTP密钥不匹配
                    self.last_error = "INVALID_KEY"
                    self.last_error_message = f"TOTP密钥错误，与数据库中存储的密钥不匹配\n输入: '{input_key}'\n存储: '{stored_key}'"
                    print(f"打开数据库失败: {self.last_error_message}")
                    return False
                else:
                    print("调试信息 - TOTP密钥验证通过")
            
            # 启动自动同步
            if self.cloud_sync.is_cloud_enabled():
                self.cloud_sync.start_auto_sync()
            
            return True
        
        except FileNotFoundError as e:
            self.last_error = "FILE_NOT_FOUND"
            self.last_error_message = f"数据库文件不存在: {str(e)}"
            print(f"打开数据库失败: {self.last_error_message}")
            return False
        except PermissionError as e:
            self.last_error = "PERMISSION_DENIED"
            self.last_error_message = f"没有权限访问数据库文件: {str(e)}"
            print(f"打开数据库失败: {self.last_error_message}")
            return False
        except Exception as e:
            self.last_error = "UNKNOWN_ERROR"
            self.last_error_message = f"未知错误: {str(e)}"
            print(f"打开数据库失败: {self.last_error_message}")
            return False
    
    def save(self):
        """保存密码数据库"""
        try:
            # 更新最后修改时间
            self.data["last_modified"] = datetime.now().isoformat()
            
            # 转换为JSON
            json_data = json.dumps(self.data, ensure_ascii=False)
            
            # 加密数据
            encrypted_data = Encryption.encrypt(json_data, self.key)
            
            # 创建备份
            if os.path.exists(self.db_path):
                self._create_backup()
            
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
            
            # 写入文件（盐值 + 加密数据）
            with open(self.db_path, "wb") as f:
                f.write(self.salt + encrypted_data)
            
            # 如果启用了云存储，同步到远程
            if self.cloud_sync.is_cloud_enabled() and self.config.get_cloud_config("sync_on_save"):
                self.cloud_sync.sync_to_remote(self.db_path)
            
            return True
        
        except Exception as e:
            print(f"保存数据库失败: {e}")
            return False
    
    def _create_backup(self):
        """创建数据库备份"""
        if not self.config.get("backup_enabled", True):
            return
        
        try:
            # 获取备份目录
            backup_path = self.config.get("backup_path", "")
            if not backup_path:
                backup_path = os.path.join(os.path.dirname(self.db_path), "backups")
            
            # 确保备份目录存在
            os.makedirs(backup_path, exist_ok=True)
            
            # 创建备份文件名（使用时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            db_name = os.path.basename(self.db_path)
            backup_file = os.path.join(backup_path, f"{os.path.splitext(db_name)[0]}_{timestamp}.bak")
            
            # 复制文件
            shutil.copy2(self.db_path, backup_file)
            
            # 清理旧备份
            self._cleanup_backups(backup_path)
            
        except Exception as e:
            print(f"创建备份失败: {e}")
    
    def _cleanup_backups(self, backup_path):
        """清理旧备份文件"""
        try:
            # 获取保留的备份数量
            backup_count = self.config.get("backup_count", 5)
            
            # 获取所有备份文件
            backup_files = []
            for f in os.listdir(backup_path):
                if f.endswith(".bak"):
                    full_path = os.path.join(backup_path, f)
                    backup_files.append((full_path, os.path.getmtime(full_path)))
            
            # 按修改时间排序
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # 删除多余的备份
            for path, _ in backup_files[backup_count:]:
                os.remove(path)
                
        except Exception as e:
            print(f"清理备份失败: {e}")
    
    def add_password(self, password_data):
        """添加新密码"""
        # 生成唯一ID
        password_id = str(int(time.time() * 1000))
        password_data["id"] = password_id
        password_data["created_at"] = datetime.now().isoformat()
        password_data["updated_at"] = datetime.now().isoformat()
        
        # 添加到数据库
        self.data["passwords"].append(password_data)
        
        # 保存数据库
        return self.save()
    
    def update_password(self, password_id, password_data):
        """更新密码"""
        for i, pwd in enumerate(self.data["passwords"]):
            if pwd["id"] == password_id:
                # 保留原始ID和创建时间
                password_data["id"] = password_id
                password_data["created_at"] = pwd["created_at"]
                password_data["updated_at"] = datetime.now().isoformat()
                
                # 更新密码
                self.data["passwords"][i] = password_data
                
                # 保存数据库
                return self.save()
        
        return False
    
    def delete_password(self, password_id):
        """删除密码"""
        for i, pwd in enumerate(self.data["passwords"]):
            if pwd["id"] == password_id:
                # 删除密码
                del self.data["passwords"][i]
                
                # 保存数据库
                return self.save()
        
        return False
    
    def get_password(self, password_id):
        """获取密码"""
        for pwd in self.data["passwords"]:
            if pwd["id"] == password_id:
                return pwd
        
        return None
    
    def get_all_passwords(self):
        """获取所有密码"""
        return self.data["passwords"]
    
    def search_passwords(self, query):
        """搜索密码"""
        query = query.lower()
        results = []
        
        for pwd in self.data["passwords"]:
            # 搜索标题、用户名、网址、备注
            if (query in pwd.get("title", "").lower() or
                query in pwd.get("username", "").lower() or
                query in pwd.get("url", "").lower() or
                query in pwd.get("notes", "").lower()):
                results.append(pwd)
        
        return results
    
    def get_passwords_by_category(self, category):
        """按分类获取密码"""
        return [pwd for pwd in self.data["passwords"] if pwd.get("category") == category]
    
    def get_categories(self):
        """获取所有分类"""
        return self.data["categories"]
        
    def update_totp_secret(self, totp_secret, username=""):
        """更新TOTP密钥"""
        self.data["totp_secret"] = totp_secret
        self.data["username"] = username
        return self.save()
    
    def add_category(self, category):
        """添加分类"""
        if category not in self.data["categories"]:
            self.data["categories"].append(category)
            return self.save()
        return True
    
    def delete_category(self, category):
        """删除分类"""
        if category in self.data["categories"]:
            # 删除分类
            self.data["categories"].remove(category)
            
            # 将该分类下的密码移动到"其他"分类
            for pwd in self.data["passwords"]:
                if pwd.get("category") == category:
                    pwd["category"] = "其他"
            
            return self.save()
        return False
    
    def rename_category(self, old_name, new_name):
        """重命名分类"""
        if old_name not in self.data["categories"]:
            return False
        
        if new_name in self.data["categories"]:
            return False  # 新名称已存在
        
        # 更新分类列表
        category_index = self.data["categories"].index(old_name)
        self.data["categories"][category_index] = new_name
        
        # 更新所有密码的分类
        for pwd in self.data["passwords"]:
            if pwd.get("category") == old_name:
                pwd["category"] = new_name
        
        return self.save()
    
    def export_data(self, export_path, password):
        """导出加密数据"""
        try:
            # 生成导出密钥
            export_key, export_salt = Encryption.generate_key(password)
            
            # 转换为JSON
            json_data = json.dumps(self.data, ensure_ascii=False)
            
            # 加密数据
            encrypted_data = Encryption.encrypt(json_data, export_key)
            
            # 写入文件（盐值 + 加密数据）
            with open(export_path, "wb") as f:
                f.write(export_salt + encrypted_data)
            
            return True
        
        except Exception as e:
            print(f"导出数据失败: {e}")
            return False
    
    def import_data(self, import_path, password):
        """导入加密数据"""
        try:
            # 读取加密的数据文件
            with open(import_path, "rb") as f:
                encrypted_data = f.read()
            
            # 读取盐值（存储在文件开头）
            salt = encrypted_data[:16]
            encrypted_content = encrypted_data[16:]
            
            # 生成密钥
            import_key, _ = Encryption.generate_key(password, salt)
            
            # 解密数据
            decrypted_data = Encryption.decrypt(encrypted_content, import_key)
            if not decrypted_data:
                return False
            
            # 解析JSON数据
            imported_data = json.loads(decrypted_data)
            
            # 合并数据
            self._merge_data(imported_data)
            
            # 保存数据库
            return self.save()
        
        except Exception as e:
            print(f"导入数据失败: {e}")
            return False
    
    def _merge_data(self, imported_data):
        """合并导入的数据"""
        # 合并分类
        for category in imported_data.get("categories", []):
            if category not in self.data["categories"]:
                self.data["categories"].append(category)
        
        # 合并密码（按ID去重）
        existing_ids = {pwd["id"] for pwd in self.data["passwords"]}
        
        for pwd in imported_data.get("passwords", []):
            if pwd["id"] not in existing_ids:
                self.data["passwords"].append(pwd)
            else:
                # 如果ID已存在，检查更新时间
                for i, existing_pwd in enumerate(self.data["passwords"]):
                    if existing_pwd["id"] == pwd["id"]:
                        # 如果导入的密码更新时间更晚，则更新
                        import_time = datetime.fromisoformat(pwd["updated_at"])
                        existing_time = datetime.fromisoformat(existing_pwd["updated_at"])
                        
                        if import_time > existing_time:
                            self.data["passwords"][i] = pwd
                        
                        break
    
    def close(self):
        """关闭数据库"""
        # 停止自动同步
        if hasattr(self, 'cloud_sync'):
            self.cloud_sync.stop_auto_sync()
    
    def manual_sync(self):
        """手动同步"""
        if hasattr(self, 'cloud_sync'):
            # 传递当前数据库文件路径给云同步
            if hasattr(self, 'db_path') and self.db_path:
                print(f"手动同步使用数据库路径: {self.db_path}")
                # 先同步到远程
                success = self.cloud_sync.sync_to_remote(self.db_path)
                if success:
                    return True, "同步到远程成功"
                else:
                    return False, "同步到远程失败"
            else:
                return self.cloud_sync.manual_sync()
        return False, "云同步未初始化"
    
    def get_sync_status(self):
        """获取同步状态"""
        if hasattr(self, 'cloud_sync'):
            return self.cloud_sync.get_sync_status()
        return "未启用"