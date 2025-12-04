#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块
"""

import os
import json
from pathlib import Path


class Config:
    """配置管理类，负责加载和保存应用程序配置"""
    
    def __init__(self):
        # 默认配置
        self.default_config = {
            "database_path": "",  # 数据库文件路径
            "theme": "dark",    # 主题 (light/dark)
            "language": "zh_CN", # 语言
            "auto_lock": True,    # 自动锁定
            "lock_timeout": 180,  # 自动锁定超时时间(秒)
            "backup_enabled": True, # 是否启用自动备份
            "backup_interval": 7,   # 备份间隔(天)
            "backup_count": 5,      # 保留备份数量
            "backup_path": "",      # 备份路径
            "save_totp_key": False,  # 是否保存TOTP密钥
            "saved_totp_key": "",   # 保存的TOTP密钥
            "column_widths": {      # 密码列表列宽
                "title": 170,       # 标题列宽
                "username": 170,    # 用户名列宽
                "url": 180,        # 网址列宽
                "modified": 180     # 最后修改时间列宽
            },
            # 云存储和网络驱动器配置
            "cloud_storage": {
                "enabled": False,           # 是否启用云存储
                "type": "local",           # 存储类型: local, baidu_netdisk, onedrive, dropbox, network_drive
                "sync_on_save": True,      # 保存时自动同步
                "sync_on_open": True,      # 打开时自动同步
                "auto_sync_interval": 300, # 自动同步间隔(秒)，0表示禁用
                "conflict_resolution": "newer", # 冲突解决策略: newer, local, remote, ask
                "local_cache_path": "",    # 本地缓存路径
                "remote_path": "",         # 远程路径
                "network_drive_path": "",  # 网络驱动器路径
                "last_sync_time": None,    # 最后同步时间
                "sync_enabled": True       # 是否启用同步功能
            }
        }
        
        # 当前配置
        self.config = self.default_config.copy()
        
        # 配置文件路径
        self.config_dir = self._get_config_dir()
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        # 确保配置目录存在
        os.makedirs(self.config_dir, exist_ok=True)
    
    def _get_config_dir(self):
        """获取配置目录"""
        # 在用户主目录下创建配置目录
        home_dir = str(Path.home())
        return os.path.join(home_dir, ".passwordmanager")
    
    def load(self):
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # 更新配置，保留默认值
                    self._merge_config(loaded_config)
                return True
        except Exception as e:
            print(f"加载配置失败: {e}")
        return False
    
    def _merge_config(self, loaded_config):
        """合并配置，确保新增的配置项有默认值"""
        def merge_dict(default, loaded):
            for key, value in default.items():
                if key in loaded:
                    if isinstance(value, dict) and isinstance(loaded[key], dict):
                        merge_dict(value, loaded[key])
                    else:
                        default[key] = loaded[key]
        
        merge_dict(self.config, loaded_config)
    
    def save(self):
        """保存配置"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
        return self.save()
    
    def get_cloud_config(self, key=None):
        """获取云存储配置"""
        cloud_config = self.config.get("cloud_storage", {})
        if key:
            return cloud_config.get(key)
        return cloud_config
    
    def set_cloud_config(self, key, value):
        """设置云存储配置"""
        if "cloud_storage" not in self.config:
            self.config["cloud_storage"] = {}
        self.config["cloud_storage"][key] = value
        return self.save()
    
    def reset(self):
        """重置配置为默认值"""
        self.config = self.default_config.copy()
        return self.save()
    
    def get_effective_database_path(self):
        """获取有效的数据库路径（考虑云存储配置）"""
        cloud_config = self.get_cloud_config()
        
        # 获取原始数据库路径和文件名
        original_db_path = self.get("database_path", "")
        if original_db_path:
            db_filename = os.path.basename(original_db_path)
        else:
            db_filename = "passwords.db"  # 默认文件名
        
        if cloud_config.get("enabled", False):
            storage_type = cloud_config.get("type", "local")
            
            if storage_type == "network_drive":
                # 网络驱动器路径
                network_path = cloud_config.get("network_drive_path", "")
                if network_path and os.path.exists(network_path):
                    return os.path.join(network_path, db_filename)
            
            elif storage_type in ["baidu_netdisk", "onedrive", "dropbox"]:
                # 云存储路径
                remote_path = cloud_config.get("remote_path", "")
                if remote_path and os.path.exists(remote_path):
                    return os.path.join(remote_path, db_filename)
            
            # 如果云存储路径不可用，使用本地缓存
            cache_path = cloud_config.get("local_cache_path", "")
            if cache_path:
                os.makedirs(cache_path, exist_ok=True)
                return os.path.join(cache_path, db_filename)
        
        # 默认使用配置的数据库路径
        if not original_db_path:
            # 如果没有配置路径，使用默认路径
            original_db_path = os.path.join(self.config_dir, db_filename)
        
        return original_db_path