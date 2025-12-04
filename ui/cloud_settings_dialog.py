#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
云存储配置对话框
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFileDialog, QMessageBox, QFormLayout, 
    QGroupBox, QCheckBox, QSpinBox, QComboBox, QTextEdit,
    QTabWidget, QWidget, QProgressBar, QFrame
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread


class CloudSyncThread(QThread):
    """云同步线程"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, cloud_sync, action):
        super().__init__()
        self.cloud_sync = cloud_sync
        self.action = action  # 'sync_to_remote', 'sync_from_remote', 'manual_sync'
    
    def run(self):
        try:
            if self.action == 'sync_to_remote':
                self.progress.emit("正在同步到远程...")
                success = self.cloud_sync.sync_to_remote()
                self.finished.emit(success, "同步到远程完成" if success else "同步到远程失败")
            
            elif self.action == 'sync_from_remote':
                self.progress.emit("正在从远程同步...")
                success = self.cloud_sync.sync_from_remote()
                self.finished.emit(success, "从远程同步完成" if success else "从远程同步失败")
            
            elif self.action == 'manual_sync':
                self.progress.emit("正在执行手动同步...")
                success, message = self.cloud_sync.manual_sync()
                self.finished.emit(success, message)
                
        except Exception as e:
            self.finished.emit(False, f"同步失败: {str(e)}")


class CloudSettingsDialog(QDialog):
    """云存储配置对话框"""
    
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.config = config
        self.cloud_sync = None
        
        # 从主窗口获取云同步管理器
        if parent and hasattr(parent, 'cloud_sync_manager'):
            self.cloud_sync = parent.cloud_sync_manager
        # 兼容旧的方式（如果有数据库实例）
        elif parent and hasattr(parent, 'database') and parent.database and hasattr(parent.database, 'cloud_sync'):
            self.cloud_sync = parent.database.cloud_sync
        
        self.setWindowTitle("云存储配置")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        # 应用主题
        if parent and hasattr(parent, 'config'):
            theme = parent.config.get("theme", "light")
            self.apply_theme(theme)
        
        self.setup_ui()
        self.load_settings()
        
        # 状态更新定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_sync_status)
        self.status_timer.start(5000)  # 每5秒更新一次状态
        
        # 立即更新一次状态
        self.update_sync_status()
    
    def apply_theme(self, theme):
        """应用主题"""
        if theme == "dark":
            self.setStyleSheet("""
                QDialog, QWidget { 
                    background-color: #2b2b2b; 
                    color: #ffffff; 
                    font-size: 14px;
                }
                QLabel { 
                    color: #ffffff; 
                    font-size: 14px;
                    padding: 2px;
                }
                QLineEdit, QSpinBox, QComboBox, QTextEdit { 
                    background-color: #3b3b3b; 
                    color: #ffffff; 
                    border: 1px solid #555555;
                    padding: 6px;
                    font-size: 14px;
                    border-radius: 3px;
                }
                QPushButton { 
                    background-color: #0d47a1; 
                    color: white; 
                    border: none; 
                    padding: 8px 15px;
                    border-radius: 4px;
                    font-size: 14px;
                    min-height: 25px;
                }
                QPushButton:hover { background-color: #1565c0; }
                QPushButton:pressed { background-color: #0a3d91; }
                QPushButton:disabled { 
                    background-color: #555555; 
                    color: #888888; 
                }
                QGroupBox { 
                    border: 1px solid #555555; 
                    color: #ffffff; 
                    margin-top: 15px; 
                    padding: 15px;
                    font-size: 14px;
                    border-radius: 5px;
                }
                QGroupBox::title { 
                    color: #ffffff; 
                    font-size: 15px;
                    font-weight: bold;
                    padding: 0 5px;
                }
                QCheckBox { 
                    color: #ffffff; 
                    font-size: 14px;
                }
                QTabWidget::pane {
                    border: 1px solid #555555;
                    background-color: #2b2b2b;
                }
                QTabBar::tab {
                    background-color: #3b3b3b;
                    color: #ffffff;
                    padding: 8px 15px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #0d47a1;
                }
                QProgressBar {
                    border: 1px solid #555555;
                    border-radius: 3px;
                    text-align: center;
                    color: #ffffff;
                }
                QProgressBar::chunk {
                    background-color: #0d47a1;
                    border-radius: 2px;
                }
            """)
        else:  # light theme
            self.setStyleSheet("""
                QDialog, QWidget { 
                    background-color: #ffffff; 
                    color: #000000; 
                    font-size: 14px;
                }
                QLabel { 
                    color: #000000; 
                    font-size: 14px;
                    padding: 2px;
                }
                QLineEdit, QSpinBox, QComboBox, QTextEdit { 
                    background-color: #ffffff; 
                    color: #000000; 
                    border: 1px solid #cccccc;
                    padding: 6px;
                    font-size: 14px;
                    border-radius: 3px;
                }
                QPushButton { 
                    background-color: #1976d2; 
                    color: white; 
                    border: none; 
                    padding: 8px 15px;
                    border-radius: 4px;
                    font-size: 14px;
                    min-height: 25px;
                }
                QPushButton:hover { background-color: #1e88e5; }
                QPushButton:pressed { background-color: #1565c0; }
                QPushButton:disabled { 
                    background-color: #cccccc; 
                    color: #666666; 
                }
                QGroupBox { 
                    border: 1px solid #cccccc; 
                    color: #000000; 
                    margin-top: 15px; 
                    padding: 15px;
                    font-size: 14px;
                    border-radius: 5px;
                }
                QGroupBox::title { 
                    color: #000000; 
                    font-size: 15px;
                    font-weight: bold;
                    padding: 0 5px;
                }
                QCheckBox { 
                    color: #000000; 
                    font-size: 14px;
                }
                QTabWidget::pane {
                    border: 1px solid #cccccc;
                    background-color: #ffffff;
                }
                QTabBar::tab {
                    background-color: #f0f0f0;
                    color: #000000;
                    padding: 8px 15px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #1976d2;
                    color: #ffffff;
                }
                QProgressBar {
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    text-align: center;
                    color: #000000;
                }
                QProgressBar::chunk {
                    background-color: #1976d2;
                    border-radius: 2px;
                }
            """)
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 基本配置标签页
        self.basic_tab = QWidget()
        self.setup_basic_tab()
        self.tab_widget.addTab(self.basic_tab, "基本配置")
        
        # 高级配置标签页
        self.advanced_tab = QWidget()
        self.setup_advanced_tab()
        self.tab_widget.addTab(self.advanced_tab, "高级配置")
        
        # 同步状态标签页
        self.status_tab = QWidget()
        self.setup_status_tab()
        self.tab_widget.addTab(self.status_tab, "同步状态")
        
        layout.addWidget(self.tab_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.test_button = QPushButton("测试连接")
        self.test_button.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_button)
        
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
    
    def setup_basic_tab(self):
        """设置基本配置标签页"""
        layout = QVBoxLayout(self.basic_tab)
        layout.setSpacing(15)
        
        # 启用云存储
        enable_group = QGroupBox("云存储设置")
        enable_layout = QVBoxLayout(enable_group)
        
        self.enable_checkbox = QCheckBox("启用云存储同步")
        self.enable_checkbox.toggled.connect(self.on_enable_toggled)
        enable_layout.addWidget(self.enable_checkbox)
        
        layout.addWidget(enable_group)
        
        # 存储类型配置
        self.storage_group = QGroupBox("存储类型")
        storage_layout = QFormLayout(self.storage_group)
        
        self.storage_type_combo = QComboBox()
        self.storage_type_combo.addItems([
            "本地存储",
            "百度网盘", 
            "OneDrive",
            "Dropbox",
            "网络驱动器"
        ])
        self.storage_type_combo.currentTextChanged.connect(self.on_storage_type_changed)
        storage_layout.addRow("存储类型:", self.storage_type_combo)
        
        layout.addWidget(self.storage_group)
        
        # 路径配置
        self.path_group = QGroupBox("路径配置")
        path_layout = QFormLayout(self.path_group)
        
        # 本地缓存路径
        cache_layout = QHBoxLayout()
        self.cache_path_edit = QLineEdit()
        self.cache_path_edit.setPlaceholderText("选择本地缓存目录...")
        cache_layout.addWidget(self.cache_path_edit)
        
        self.cache_browse_button = QPushButton("浏览")
        self.cache_browse_button.clicked.connect(self.browse_cache_path)
        cache_layout.addWidget(self.cache_browse_button)
        
        path_layout.addRow("本地缓存:", cache_layout)
        
        # 远程路径
        remote_layout = QHBoxLayout()
        self.remote_path_edit = QLineEdit()
        self.remote_path_edit.setPlaceholderText("选择云存储同步目录...")
        remote_layout.addWidget(self.remote_path_edit)
        
        self.remote_browse_button = QPushButton("浏览")
        self.remote_browse_button.clicked.connect(self.browse_remote_path)
        remote_layout.addWidget(self.remote_browse_button)
        
        path_layout.addRow("云存储路径:", remote_layout)
        
        layout.addWidget(self.path_group)
        
        layout.addStretch()
    
    def setup_advanced_tab(self):
        """设置高级配置标签页"""
        layout = QVBoxLayout(self.advanced_tab)
        layout.setSpacing(15)
        
        # 同步选项
        sync_group = QGroupBox("同步选项")
        sync_layout = QFormLayout(sync_group)
        
        self.sync_on_save_checkbox = QCheckBox("保存时自动同步")
        sync_layout.addRow("", self.sync_on_save_checkbox)
        
        self.sync_on_open_checkbox = QCheckBox("打开时自动同步")
        sync_layout.addRow("", self.sync_on_open_checkbox)
        
        self.auto_sync_interval_spinbox = QSpinBox()
        self.auto_sync_interval_spinbox.setRange(0, 3600)
        self.auto_sync_interval_spinbox.setSuffix(" 秒")
        self.auto_sync_interval_spinbox.setSpecialValueText("禁用")
        sync_layout.addRow("自动同步间隔:", self.auto_sync_interval_spinbox)
        
        layout.addWidget(sync_group)
        
        # 冲突解决
        conflict_group = QGroupBox("冲突解决")
        conflict_layout = QFormLayout(conflict_group)
        
        self.conflict_combo = QComboBox()
        self.conflict_combo.addItems([
            "使用较新文件",
            "优先本地文件", 
            "优先远程文件",
            "每次询问"
        ])
        conflict_layout.addRow("冲突策略:", self.conflict_combo)
        
        layout.addWidget(conflict_group)
        
        # 其他选项
        other_group = QGroupBox("其他选项")
        other_layout = QFormLayout(other_group)
        
        self.sync_enabled_checkbox = QCheckBox("启用同步功能")
        other_layout.addRow("", self.sync_enabled_checkbox)
        
        layout.addWidget(other_group)
        
        layout.addStretch()
    
    def setup_status_tab(self):
        """设置同步状态标签页"""
        layout = QVBoxLayout(self.status_tab)
        layout.setSpacing(15)
        
        # 状态信息
        status_group = QGroupBox("同步状态")
        status_layout = QFormLayout(status_group)
        
        self.status_label = QLabel("未知")
        status_layout.addRow("当前状态:", self.status_label)
        
        self.last_sync_label = QLabel("从未同步")
        status_layout.addRow("最后同步:", self.last_sync_label)
        
        self.connection_label = QLabel("未测试")
        status_layout.addRow("连接状态:", self.connection_label)
        
        layout.addWidget(status_group)
        
        # 手动操作
        manual_group = QGroupBox("手动操作")
        manual_layout = QVBoxLayout(manual_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        manual_layout.addWidget(self.progress_bar)
        
        # 状态文本
        self.operation_status_label = QLabel("")
        manual_layout.addWidget(self.operation_status_label)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        self.sync_from_remote_button = QPushButton("从远程同步")
        self.sync_from_remote_button.clicked.connect(self.sync_from_remote)
        button_layout.addWidget(self.sync_from_remote_button)
        
        self.sync_to_remote_button = QPushButton("同步到远程")
        self.sync_to_remote_button.clicked.connect(self.sync_to_remote)
        button_layout.addWidget(self.sync_to_remote_button)
        
        self.manual_sync_button = QPushButton("完整同步")
        self.manual_sync_button.clicked.connect(self.manual_sync)
        button_layout.addWidget(self.manual_sync_button)
        
        manual_layout.addLayout(button_layout)
        
        layout.addWidget(manual_group)
        
        layout.addStretch()
    
    def on_enable_toggled(self, checked):
        """启用状态改变"""
        self.storage_group.setEnabled(checked)
        self.path_group.setEnabled(checked)
        
        # 更新高级选项卡的控件状态
        for widget in [self.sync_on_save_checkbox, self.sync_on_open_checkbox, 
                      self.auto_sync_interval_spinbox, self.conflict_combo, 
                      self.sync_enabled_checkbox]:
            widget.setEnabled(checked)
        
        # 更新状态选项卡的按钮状态
        for button in [self.sync_from_remote_button, self.sync_to_remote_button, 
                      self.manual_sync_button]:
            button.setEnabled(checked)
    
    def on_storage_type_changed(self, storage_type):
        """存储类型改变"""
        if storage_type == "本地存储":
            self.remote_path_edit.setPlaceholderText("本地存储不需要远程路径")
            self.remote_path_edit.setEnabled(False)
            self.remote_browse_button.setEnabled(False)
        elif storage_type == "百度网盘":
            self.remote_path_edit.setPlaceholderText("例如: C:\\Users\\用户名\\BaiduNetdiskDownload\\PasswordManager")
            self.remote_path_edit.setEnabled(True)
            self.remote_browse_button.setEnabled(True)
        elif storage_type == "OneDrive":
            self.remote_path_edit.setPlaceholderText("例如: C:\\Users\\用户名\\OneDrive\\PasswordManager")
            self.remote_path_edit.setEnabled(True)
            self.remote_browse_button.setEnabled(True)
        elif storage_type == "Dropbox":
            self.remote_path_edit.setPlaceholderText("例如: C:\\Users\\用户名\\Dropbox\\PasswordManager")
            self.remote_path_edit.setEnabled(True)
            self.remote_browse_button.setEnabled(True)
        elif storage_type == "网络驱动器":
            self.remote_path_edit.setPlaceholderText("例如: \\\\服务器\\共享文件夹\\PasswordManager")
            self.remote_path_edit.setEnabled(True)
            self.remote_browse_button.setEnabled(True)
    
    def browse_cache_path(self):
        """浏览本地缓存路径"""
        path = QFileDialog.getExistingDirectory(
            self, "选择本地缓存目录", self.cache_path_edit.text()
        )
        if path:
            self.cache_path_edit.setText(path)
    
    def browse_remote_path(self):
        """浏览远程路径"""
        path = QFileDialog.getExistingDirectory(
            self, "选择云存储目录", self.remote_path_edit.text()
        )
        if path:
            self.remote_path_edit.setText(path)
    
    def test_connection(self):
        """测试连接"""
        if not self.enable_checkbox.isChecked():
            QMessageBox.warning(self, "警告", "请先启用云存储")
            return
        
        storage_type = self.storage_type_combo.currentText()
        remote_path = self.remote_path_edit.text().strip()
        
        if storage_type != "本地存储" and not remote_path:
            QMessageBox.warning(self, "警告", "请设置云存储路径")
            return
        
        try:
            if storage_type == "本地存储":
                self.connection_label.setText("本地存储 - 正常")
                QMessageBox.information(self, "测试结果", "本地存储连接正常")
            else:
                # 检查路径是否存在和可写
                if os.path.exists(remote_path) and os.access(remote_path, os.W_OK):
                    self.connection_label.setText("连接正常")
                    QMessageBox.information(self, "测试结果", f"{storage_type} 连接正常")
                else:
                    self.connection_label.setText("连接失败")
                    QMessageBox.warning(self, "测试结果", f"{storage_type} 路径不存在或无写入权限")
        
        except Exception as e:
            self.connection_label.setText("连接失败")
            QMessageBox.critical(self, "测试失败", f"连接测试失败: {str(e)}")
    
    def sync_from_remote(self):
        """从远程同步"""
        if not self.cloud_sync:
            QMessageBox.warning(self, "警告", "云同步功能未初始化")
            return
        
        self.start_sync_operation('sync_from_remote')
    
    def sync_to_remote(self):
        """同步到远程"""
        if not self.cloud_sync:
            QMessageBox.warning(self, "警告", "云同步功能未初始化")
            return
        
        self.start_sync_operation('sync_to_remote')
    
    def manual_sync(self):
        """手动完整同步"""
        if not self.cloud_sync:
            QMessageBox.warning(self, "警告", "云同步功能未初始化")
            return
        
        self.start_sync_operation('manual_sync')
    
    def start_sync_operation(self, action):
        """启动同步操作"""
        # 禁用按钮
        for button in [self.sync_from_remote_button, self.sync_to_remote_button, 
                      self.manual_sync_button]:
            button.setEnabled(False)
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        
        # 启动同步线程
        self.sync_thread = CloudSyncThread(self.cloud_sync, action)
        self.sync_thread.progress.connect(self.operation_status_label.setText)
        self.sync_thread.finished.connect(self.on_sync_finished)
        self.sync_thread.start()
    
    def on_sync_finished(self, success, message):
        """同步完成"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
        # 启用按钮
        for button in [self.sync_from_remote_button, self.sync_to_remote_button, 
                      self.manual_sync_button]:
            button.setEnabled(True)
        
        # 显示结果
        self.operation_status_label.setText(message)
        
        if success:
            QMessageBox.information(self, "同步完成", message)
        else:
            QMessageBox.warning(self, "同步失败", message)
        
        # 更新状态
        self.update_sync_status()
    
    def update_sync_status(self):
        """更新同步状态"""
        if not hasattr(self, 'status_label'):
            return
            
        if not self.cloud_sync:
            self.status_label.setText("未知 (云同步功能未初始化)")
            if hasattr(self, 'last_sync_label'):
                self.last_sync_label.setText("未知")
            return
        
        try:
            status = self.cloud_sync.get_sync_status()
            self.status_label.setText(status)
            
            # 更新最后同步时间
            if self.config:
                last_sync = self.config.get_cloud_config("last_sync_time")
                if last_sync:
                    try:
                        from datetime import datetime
                        sync_time = datetime.fromisoformat(last_sync)
                        if hasattr(self, 'last_sync_label'):
                            self.last_sync_label.setText(sync_time.strftime('%Y-%m-%d %H:%M:%S'))
                    except:
                        if hasattr(self, 'last_sync_label'):
                            self.last_sync_label.setText("时间格式错误")
                else:
                    if hasattr(self, 'last_sync_label'):
                        self.last_sync_label.setText("从未同步")
        except Exception as e:
            self.status_label.setText(f"状态获取失败: {str(e)}")
            if hasattr(self, 'last_sync_label'):
                self.last_sync_label.setText("未知")
    
    def load_settings(self):
        """加载设置"""
        if not self.config:
            return
        
        cloud_config = self.config.get_cloud_config()
        
        # 基本设置
        self.enable_checkbox.setChecked(cloud_config.get("enabled", False))
        
        storage_type_map = {
            "local": "本地存储",
            "baidu_netdisk": "百度网盘",
            "onedrive": "OneDrive", 
            "dropbox": "Dropbox",
            "network_drive": "网络驱动器"
        }
        
        storage_type = cloud_config.get("type", "local")
        display_type = storage_type_map.get(storage_type, "本地存储")
        index = self.storage_type_combo.findText(display_type)
        if index >= 0:
            self.storage_type_combo.setCurrentIndex(index)
        
        self.cache_path_edit.setText(cloud_config.get("local_cache_path", ""))
        
        if storage_type == "network_drive":
            self.remote_path_edit.setText(cloud_config.get("network_drive_path", ""))
        else:
            self.remote_path_edit.setText(cloud_config.get("remote_path", ""))
        
        # 高级设置
        self.sync_on_save_checkbox.setChecked(cloud_config.get("sync_on_save", True))
        self.sync_on_open_checkbox.setChecked(cloud_config.get("sync_on_open", True))
        self.auto_sync_interval_spinbox.setValue(cloud_config.get("auto_sync_interval", 300))
        
        conflict_map = {
            "newer": "使用较新文件",
            "local": "优先本地文件",
            "remote": "优先远程文件", 
            "ask": "每次询问"
        }
        
        conflict_resolution = cloud_config.get("conflict_resolution", "newer")
        display_conflict = conflict_map.get(conflict_resolution, "使用较新文件")
        index = self.conflict_combo.findText(display_conflict)
        if index >= 0:
            self.conflict_combo.setCurrentIndex(index)
        
        self.sync_enabled_checkbox.setChecked(cloud_config.get("sync_enabled", True))
        
        # 触发启用状态更新
        self.on_enable_toggled(self.enable_checkbox.isChecked())
        self.on_storage_type_changed(self.storage_type_combo.currentText())
        
        # 更新状态
        self.update_sync_status()
    
    def save_settings(self):
        """保存设置"""
        if not self.config:
            QMessageBox.warning(self, "错误", "配置对象未初始化")
            return
        
        try:
            # 映射存储类型
            storage_type_map = {
                "本地存储": "local",
                "百度网盘": "baidu_netdisk",
                "OneDrive": "onedrive",
                "Dropbox": "dropbox", 
                "网络驱动器": "network_drive"
            }
            
            # 映射冲突解决策略
            conflict_map = {
                "使用较新文件": "newer",
                "优先本地文件": "local",
                "优先远程文件": "remote",
                "每次询问": "ask"
            }
            
            storage_type = storage_type_map[self.storage_type_combo.currentText()]
            conflict_resolution = conflict_map[self.conflict_combo.currentText()]
            
            # 保存配置
            self.config.set_cloud_config("enabled", self.enable_checkbox.isChecked())
            self.config.set_cloud_config("type", storage_type)
            self.config.set_cloud_config("sync_on_save", self.sync_on_save_checkbox.isChecked())
            self.config.set_cloud_config("sync_on_open", self.sync_on_open_checkbox.isChecked())
            self.config.set_cloud_config("auto_sync_interval", self.auto_sync_interval_spinbox.value())
            self.config.set_cloud_config("conflict_resolution", conflict_resolution)
            self.config.set_cloud_config("local_cache_path", self.cache_path_edit.text().strip())
            self.config.set_cloud_config("sync_enabled", self.sync_enabled_checkbox.isChecked())
            
            # 修复：使用映射后的英文值进行比较
            if storage_type == "network_drive":
                self.config.set_cloud_config("network_drive_path", self.remote_path_edit.text().strip())
            else:
                self.config.set_cloud_config("remote_path", self.remote_path_edit.text().strip())
            
            QMessageBox.information(self, "成功", "云存储配置保存成功！\n重启应用程序后生效。")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}")
    
    def closeEvent(self, event):
        """关闭事件"""
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()
        event.accept()