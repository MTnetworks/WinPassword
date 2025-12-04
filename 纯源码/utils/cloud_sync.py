#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
云存储同步管理模块
"""

import os
import shutil
import time
import threading
from datetime import datetime
from pathlib import Path


class CloudSyncManager:
    """云存储同步管理器"""
    
    def __init__(self, config):
        self.config = config
        self.sync_lock = threading.Lock()
        self.auto_sync_timer = None
        self.is_syncing = False
    
    def is_cloud_enabled(self):
        """检查是否启用云存储"""
        return self.config.get_cloud_config("enabled")
    
    def get_storage_type(self):
        """获取存储类型"""
        return self.config.get_cloud_config("type")
    
    def _get_database_filename(self):
        """获取数据库文件名"""
        # 从配置中获取原始数据库路径
        original_db_path = self.config.get("database_path", "")
        if original_db_path:
            return os.path.basename(original_db_path)
        else:
            return "passwords.db"  # 默认文件名
    
    def get_local_path(self):
        """获取本地缓存路径"""
        cache_path = self.config.get_cloud_config("local_cache_path")
        if not cache_path:
            # 使用默认缓存路径
            cache_path = os.path.join(self.config._get_config_dir(), "cache")
        
        os.makedirs(cache_path, exist_ok=True)
        db_filename = self._get_database_filename()
        return os.path.join(cache_path, db_filename)
    
    def get_remote_path(self):
        """获取远程路径"""
        storage_type = self.get_storage_type()
        db_filename = self._get_database_filename()
        
        if storage_type == "network_drive":
            network_path = self.config.get_cloud_config("network_drive_path")
            if network_path:
                return os.path.join(network_path, db_filename)
        
        elif storage_type in ["baidu_netdisk", "onedrive", "dropbox"]:
            remote_path = self.config.get_cloud_config("remote_path")
            if remote_path:
                return os.path.join(remote_path, db_filename)
        
        return None
    
    def check_remote_accessibility(self):
        """检查远程路径是否可访问"""
        remote_path = self.get_remote_path()
        if not remote_path:
            return False
        
        try:
            # 检查远程目录是否存在
            remote_dir = os.path.dirname(remote_path)
            return os.path.exists(remote_dir) and os.access(remote_dir, os.W_OK)
        except Exception:
            return False
    
    def sync_to_remote(self, local_file_path=None):
        """同步到远程"""
        if not self.is_cloud_enabled():
            return True
        
        with self.sync_lock:
            try:
                self.is_syncing = True
                
                if not local_file_path:
                    # 如果没有指定本地文件路径，优先使用当前数据库路径
                    # 从配置中获取当前使用的数据库路径
                    current_db_path = self.config.get("database_path")
                    if current_db_path and os.path.exists(current_db_path):
                        local_file_path = current_db_path
                        print(f"使用当前数据库路径进行同步: {local_file_path}")
                    else:
                        # 回退到有效的数据库路径
                        local_file_path = self.config.get_effective_database_path()
                        print(f"使用有效数据库路径进行同步: {local_file_path}")
                
                remote_path = self.get_remote_path()
                if not remote_path:
                    print("无法获取远程路径")
                    return False
                
                # 检查远程路径是否可访问
                if not self.check_remote_accessibility():
                    print("远程路径不可访问，跳过同步")
                    return False
                
                # 确保远程目录存在
                remote_dir = os.path.dirname(remote_path)
                try:
                    os.makedirs(remote_dir, exist_ok=True)
                except Exception as e:
                    print(f"创建远程目录失败: {e}")
                    return False
                
                # 如果本地文件存在，复制到远程
                if os.path.exists(local_file_path):
                    print(f"开始同步文件: {local_file_path} -> {remote_path}")
                    
                    # 创建临时文件，避免同步过程中文件损坏
                    temp_path = remote_path + ".tmp"
                    try:
                        shutil.copy2(local_file_path, temp_path)
                        print(f"文件复制到临时路径成功: {temp_path}")
                    except Exception as e:
                        print(f"复制文件到临时路径失败: {e}")
                        return False
                    
                    # 原子性重命名
                    try:
                        if os.path.exists(temp_path):
                            if os.path.exists(remote_path):
                                os.remove(remote_path)
                            os.rename(temp_path, remote_path)
                            print(f"文件重命名成功: {remote_path}")
                        else:
                            print("临时文件不存在，同步失败")
                            return False
                    except Exception as e:
                        print(f"文件重命名失败: {e}")
                        return False
                    
                    # 更新同步时间
                    self.config.set_cloud_config("last_sync_time", datetime.now().isoformat())
                    
                    print(f"同步到远程成功: {remote_path}")
                    return True
                else:
                    print(f"本地文件不存在: {local_file_path}")
                    return False
                
            except Exception as e:
                print(f"同步到远程失败: {e}")
                return False
            finally:
                self.is_syncing = False
    
    def sync_from_remote(self, local_file_path=None):
        """从远程同步"""
        if not self.is_cloud_enabled():
            return True
        
        with self.sync_lock:
            try:
                self.is_syncing = True
                
                if not local_file_path:
                    # 从远程同步时，需要确定真正的本地路径
                    # 获取数据库文件名
                    db_filename = self._get_database_filename()
                    
                    # 获取原始数据库路径
                    original_db_path = self.config.get("database_path")
                    
                    # 检查原始路径是否是云存储路径
                    remote_path = self.get_remote_path()
                    if original_db_path and remote_path and os.path.normpath(original_db_path) == os.path.normpath(remote_path):
                        # 如果原始路径就是云存储路径，需要构造本地路径
                        # 使用用户文档目录作为本地路径
                        user_docs = os.path.expanduser("~/Documents")
                        local_file_path = os.path.join(user_docs, db_filename)
                        print(f"检测到云存储路径，使用用户文档目录作为同步目标: {local_file_path}")
                    elif original_db_path:
                        # 如果原始路径不是云存储路径，直接使用
                        local_file_path = original_db_path
                        print(f"使用原始数据库路径作为同步目标: {local_file_path}")
                    else:
                        # 如果没有原始路径，使用默认本地路径
                        user_docs = os.path.expanduser("~/Documents")
                        local_file_path = os.path.join(user_docs, db_filename)
                        print(f"使用默认本地路径作为同步目标: {local_file_path}")
                
                remote_path = self.get_remote_path()
                if not remote_path:
                    print("无法获取远程路径")
                    return False
                
                # 如果远程文件不存在，这不是错误，返回True
                if not os.path.exists(remote_path):
                    print(f"远程文件不存在，跳过从远程同步: {remote_path}")
                    return True
                
                print(f"开始从远程同步: {remote_path} -> {local_file_path}")
                
                # 检查冲突解决策略
                conflict_resolution = self.config.get_cloud_config("conflict_resolution")
                
                if os.path.exists(local_file_path):
                    # 比较文件修改时间
                    local_mtime = os.path.getmtime(local_file_path)
                    remote_mtime = os.path.getmtime(remote_path)
                    
                    if conflict_resolution == "newer":
                        if local_mtime >= remote_mtime:
                            print("本地文件更新，跳过从远程同步")
                            return True
                    elif conflict_resolution == "local":
                        print("优先使用本地文件，跳过从远程同步")
                        return True
                    elif conflict_resolution == "remote":
                        pass  # 继续从远程同步
                    # TODO: 实现 "ask" 策略，需要UI支持
                
                # 确保本地目录存在
                local_dir = os.path.dirname(local_file_path)
                try:
                    os.makedirs(local_dir, exist_ok=True)
                    print(f"确保本地目录存在: {local_dir}")
                except Exception as e:
                    print(f"创建本地目录失败: {e}")
                    return False
                
                # 从远程复制到本地
                try:
                    print(f"开始复制文件: {remote_path} -> {local_file_path}")
                    shutil.copy2(remote_path, local_file_path)
                    print(f"文件复制成功: {local_file_path}")
                except Exception as e:
                    print(f"复制文件失败: {e}")
                    return False
                
                # 验证文件是否成功复制
                if os.path.exists(local_file_path):
                    file_size = os.path.getsize(local_file_path)
                    print(f"同步完成，本地文件大小: {file_size} 字节")
                else:
                    print("同步失败，本地文件不存在")
                    return False
                
                # 更新同步时间
                self.config.set_cloud_config("last_sync_time", datetime.now().isoformat())
                
                print(f"从远程同步成功: {remote_path} -> {local_file_path}")
                return True
                
            except Exception as e:
                print(f"从远程同步失败: {e}")
                return False
            finally:
                self.is_syncing = False
    
    def start_auto_sync(self):
        """启动自动同步"""
        if not self.is_cloud_enabled():
            return
        
        interval = self.config.get_cloud_config("auto_sync_interval")
        if interval and interval > 0:
            self.stop_auto_sync()  # 停止现有的定时器
            
            def auto_sync():
                if self.config.get_cloud_config("sync_enabled"):
                    self.sync_from_remote()
                    self.sync_to_remote()
                
                # 重新设置定时器
                self.auto_sync_timer = threading.Timer(interval, auto_sync)
                self.auto_sync_timer.daemon = True
                self.auto_sync_timer.start()
            
            self.auto_sync_timer = threading.Timer(interval, auto_sync)
            self.auto_sync_timer.daemon = True
            self.auto_sync_timer.start()
    
    def stop_auto_sync(self):
        """停止自动同步"""
        if self.auto_sync_timer:
            self.auto_sync_timer.cancel()
            self.auto_sync_timer = None
    
    def manual_sync(self):
        """手动同步"""
        if not self.is_cloud_enabled():
            return False, "云存储未启用"
        
        try:
            # 先从远程同步
            if self.config.get_cloud_config("sync_on_open"):
                success = self.sync_from_remote()
                if not success:
                    return False, "从远程同步失败"
            
            # 再同步到远程
            if self.config.get_cloud_config("sync_on_save"):
                success = self.sync_to_remote()
                if not success:
                    return False, "同步到远程失败"
            
            return True, "同步成功"
            
        except Exception as e:
            return False, f"同步失败: {e}"
    
    def get_sync_status(self):
        """获取同步状态"""
        if not self.is_cloud_enabled():
            return "未启用"
        
        if self.is_syncing:
            return "同步中..."
        
        last_sync = self.config.get_cloud_config("last_sync_time")
        if last_sync:
            try:
                sync_time = datetime.fromisoformat(last_sync)
                return f"最后同步: {sync_time.strftime('%Y-%m-%d %H:%M:%S')}"
            except:
                pass
        
        return "未同步"