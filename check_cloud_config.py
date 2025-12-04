#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
云存储配置检查脚本
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config import Config

def check_cloud_config():
    """检查云存储配置"""
    print("=" * 60)
    print("云存储配置检查")
    print("=" * 60)
    
    # 创建配置实例
    config = Config()
    config.load()
    
    print(f"配置文件路径: {config.config_file}")
    print(f"配置目录: {config.config_dir}")
    print(f"配置文件是否存在: {os.path.exists(config.config_file)}")
    print()
    
    # 检查数据库路径配置
    print("数据库路径配置:")
    print("-" * 30)
    database_path = config.get("database_path", "")
    effective_db_path = config.get_effective_database_path()
    print(f"配置的数据库路径: {database_path}")
    print(f"有效数据库路径: {effective_db_path}")
    
    # 检查数据库文件是否存在
    if effective_db_path:
        print(f"数据库文件是否存在: {os.path.exists(effective_db_path)}")
        if os.path.exists(effective_db_path):
            file_size = os.path.getsize(effective_db_path)
            mod_time = datetime.fromtimestamp(os.path.getmtime(effective_db_path))
            print(f"数据库文件大小: {file_size} 字节")
            print(f"最后修改时间: {mod_time}")
    print()
    
    # 检查云存储配置
    print("云存储配置:")
    print("-" * 30)
    cloud_config = config.get_cloud_config()
    
    for key, value in cloud_config.items():
        if key == "last_sync_time" and value:
            try:
                sync_time = datetime.fromisoformat(value)
                print(f"{key}: {sync_time} ({value})")
            except:
                print(f"{key}: {value}")
        else:
            print(f"{key}: {value}")
    print()
    
    # 检查路径是否存在
    print("路径检查:")
    print("-" * 30)
    
    if cloud_config.get("enabled", False):
        storage_type = cloud_config.get("type", "local")
        print(f"存储类型: {storage_type}")
        
        if storage_type == "network_drive":
            network_path = cloud_config.get("network_drive_path", "")
            print(f"网络驱动器路径: {network_path}")
            if network_path:
                exists = os.path.exists(network_path)
                print(f"网络驱动器路径是否存在: {exists}")
                if exists:
                    try:
                        writable = os.access(network_path, os.W_OK)
                        print(f"网络驱动器路径是否可写: {writable}")
                    except:
                        print("网络驱动器路径权限检查失败")
        
        elif storage_type in ["baidu_netdisk", "onedrive", "dropbox"]:
            remote_path = cloud_config.get("remote_path", "")
            print(f"远程路径: {remote_path}")
            if remote_path:
                exists = os.path.exists(remote_path)
                print(f"远程路径是否存在: {exists}")
                if exists:
                    try:
                        writable = os.access(remote_path, os.W_OK)
                        print(f"远程路径是否可写: {writable}")
                    except:
                        print("远程路径权限检查失败")
        
        cache_path = cloud_config.get("local_cache_path", "")
        print(f"本地缓存路径: {cache_path}")
        if cache_path:
            exists = os.path.exists(cache_path)
            print(f"本地缓存路径是否存在: {exists}")
            if exists:
                try:
                    writable = os.access(cache_path, os.W_OK)
                    print(f"本地缓存路径是否可写: {writable}")
                except:
                    print("本地缓存路径权限检查失败")
    else:
        print("云存储未启用")
    
    print()
    
    # 检查云同步管理器
    print("云同步管理器检查:")
    print("-" * 30)
    try:
        from utils.cloud_sync import CloudSyncManager
        cloud_sync = CloudSyncManager(config)
        print(f"云存储是否启用: {cloud_sync.is_cloud_enabled()}")
        print(f"存储类型: {cloud_sync.get_storage_type()}")
        print(f"本地路径: {cloud_sync.get_local_path()}")
        print(f"远程路径: {cloud_sync.get_remote_path()}")
        print(f"远程路径是否可访问: {cloud_sync.check_remote_accessibility()}")
    except Exception as e:
        print(f"云同步管理器初始化失败: {e}")
    
    print()
    
    # 检查可能的问题
    print("问题诊断:")
    print("-" * 30)
    issues = []
    
    # 检查数据库路径问题
    if database_path and not os.path.exists(database_path):
        issues.append(f"配置的数据库路径不存在: {database_path}")
    
    if effective_db_path and not os.path.exists(effective_db_path):
        issues.append(f"有效数据库路径不存在: {effective_db_path}")
    
    # 检查云存储路径问题
    if cloud_config.get("enabled", False):
        storage_type = cloud_config.get("type", "local")
        
        if storage_type == "network_drive":
            network_path = cloud_config.get("network_drive_path", "")
            if not network_path:
                issues.append("启用了网络驱动器但未配置路径")
            elif not os.path.exists(network_path):
                issues.append(f"网络驱动器路径不存在: {network_path}")
        
        elif storage_type in ["baidu_netdisk", "onedrive", "dropbox"]:
            remote_path = cloud_config.get("remote_path", "")
            if not remote_path:
                issues.append(f"启用了{storage_type}但未配置远程路径")
            elif not os.path.exists(remote_path):
                issues.append(f"远程路径不存在: {remote_path}")
    
    # 检查文件名不匹配问题
    if database_path and effective_db_path:
        original_filename = os.path.basename(database_path)
        effective_filename = os.path.basename(effective_db_path)
        if original_filename != effective_filename:
            issues.append(f"数据库文件名不匹配: 原始({original_filename}) vs 有效({effective_filename})")
    
    if issues:
        for issue in issues:
            print(f"⚠️  {issue}")
    else:
        print("✅ 未发现明显问题")
    
    print()
    
    # 显示完整配置文件内容（如果存在）
    if os.path.exists(config.config_file):
        print("完整配置文件内容:")
        print("-" * 30)
        try:
            with open(config.config_file, "r", encoding="utf-8") as f:
                config_content = json.load(f)
                print(json.dumps(config_content, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"读取配置文件失败: {e}")
    else:
        print("配置文件不存在，将使用默认配置")
        print("默认配置:")
        print(json.dumps(config.default_config, indent=2, ensure_ascii=False))
    
    print("=" * 60)

def fix_database_path_issue():
    """修复数据库路径问题"""
    print("\n尝试修复数据库路径问题...")
    
    config = Config()
    config.load()
    
    database_path = config.get("database_path", "")
    if not database_path:
        print("未配置数据库路径，无需修复")
        return
    
    # 检查原始数据库文件是否存在
    if os.path.exists(database_path):
        print(f"原始数据库文件存在: {database_path}")
        
        # 如果启用了云存储，确保云存储路径中也有正确的文件
        cloud_config = config.get_cloud_config()
        if cloud_config.get("enabled", False):
            effective_path = config.get_effective_database_path()
            if effective_path != database_path and not os.path.exists(effective_path):
                try:
                    # 确保目标目录存在
                    os.makedirs(os.path.dirname(effective_path), exist_ok=True)
                    # 复制文件
                    import shutil
                    shutil.copy2(database_path, effective_path)
                    print(f"已复制数据库文件到: {effective_path}")
                except Exception as e:
                    print(f"复制数据库文件失败: {e}")
    else:
        print(f"原始数据库文件不存在: {database_path}")

if __name__ == "__main__":
    check_cloud_config()
    
    # 询问是否尝试修复问题
    try:
        response = input("\n是否尝试修复数据库路径问题? (y/n): ").lower().strip()
        if response in ['y', 'yes', '是']:
            fix_database_path_issue()
    except KeyboardInterrupt:
        print("\n检查完成")