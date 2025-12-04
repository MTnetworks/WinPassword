#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
登录窗口模块
"""

import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QTabWidget,
    QFormLayout, QGroupBox, QCheckBox, QSpinBox, QComboBox, QInputDialog,
    QScrollArea, QSpacerItem, QSizePolicy, QMenu, QDialog
)
from PyQt6.QtGui import QPixmap, QIcon, QFont
from PyQt6.QtCore import Qt, QSize, QTimer

from utils.auth import Authenticator
from database.password_db import PasswordDatabase
from ui.main_window import MainWindow, CustomInputDialog


class LoginWindow(QMainWindow):
    """登录窗口类"""
    
    def __init__(self, config):
        super().__init__()
        
        self.config = config
        self.authenticator = Authenticator(config)
        self.db = PasswordDatabase(config)
        
        self.setWindowTitle("密码管理工具 - 登录")
        self.setMinimumSize(500, 400)
        
        # 应用主题
        self.apply_theme(self.config.get("theme", "light"))
        
        # 设置UI
        self.setup_ui()
        
        # 加载上次使用的数据库路径
        last_db_path = self.config.get("database_path", "")
        if last_db_path and os.path.exists(last_db_path):
            self.db_path_edit.setText(last_db_path)
    
    def setup_ui(self):
        """设置UI"""
        # 创建中心部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabBar::tab { 
                height: 25px; 
                min-width: 80px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                margin-bottom: -1px;
            }
        """)
        self.tab_widget.setDocumentMode(True)  # 使标签页更紧凑
        
        # 创建登录标签页
        self.login_tab = QWidget()
        self.create_login_tab()
        self.tab_widget.addTab(self.login_tab, "登录")
        
        # 创建新建标签页
        self.create_tab = QWidget()
        self.create_create_tab()
        self.tab_widget.addTab(self.create_tab, "新建")
        
        # 创建设置标签页
        self.settings_tab = QWidget()
        self.create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "设置")
        
        # 创建密钥管理标签页
        self.key_management_tab = QWidget()
        self.create_key_management_tab()
        self.tab_widget.addTab(self.key_management_tab, "密钥管理")
        
        # 创建主布局
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.tab_widget)
    
    def apply_theme(self, theme):
        """应用主题"""
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QTabWidget::pane {
                    border: 1px solid #3d3d3d;
                }
                QTabBar::tab {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                    padding: 5px 10px;
                }
                QTabBar::tab:selected {
                    background-color: #3d3d3d;
                }
                QGroupBox {
                    border: 2px solid #3d3d3d;
                    border-radius: 6px;
                    margin-top: 1em;
                    color: #ffffff;
                }
                QGroupBox::title {
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QLineEdit, QSpinBox, QComboBox {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border: 1px solid #505050;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #0d47a1;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #1565c0;
                }
                QPushButton:pressed {
                    background-color: #0a3d8f;
                }
                QCheckBox {
                    color: #ffffff;
                }
                QCheckBox::indicator {
                    background-color: #3d3d3d;
                    border: 1px solid #505050;
                    border-radius: 2px;
                }
                QCheckBox::indicator:checked {
                    background-color: #0d47a1;
                }
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                QScrollBar:vertical {
                    border: none;
                    background-color: #2b2b2b;
                    width: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background-color: #3d3d3d;
                    border-radius: 5px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                QTabWidget::pane {
                    border: 1px solid #d0d0d0;
                }
                QTabBar::tab {
                    background-color: #f0f0f0;
                    border: 1px solid #d0d0d0;
                    padding: 5px 10px;
                }
                QTabBar::tab:selected {
                    background-color: #ffffff;
                }
                QGroupBox {
                    border: 2px solid #d0d0d0;
                    border-radius: 6px;
                    margin-top: 1em;
                }
                QLineEdit, QSpinBox, QComboBox {
                    background-color: #ffffff;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #1976d2;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #1e88e5;
                }
                QPushButton:pressed {
                    background-color: #1565c0;
                }
                QCheckBox::indicator {
                    border: 1px solid #d0d0d0;
                    border-radius: 2px;
                }
                QCheckBox::indicator:checked {
                    background-color: #1976d2;
                }
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                QScrollBar:vertical {
                    border: none;
                    background-color: #f0f0f0;
                    width: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background-color: #d0d0d0;
                    border-radius: 5px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)
        
        # 创建中心部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabBar::tab { height: 30px; min-width: 100px; }")
        
        # 创建登录标签页
        self.login_tab = QWidget()
        self.create_login_tab()
        self.tab_widget.addTab(self.login_tab, "登录")
        
        # 创建新建标签页
        self.create_tab = QWidget()
        self.create_create_tab()
        self.tab_widget.addTab(self.create_tab, "新建")
        
        # 创建设置标签页
        self.settings_tab = QWidget()
        self.create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "设置")
        
        # 创建密钥管理标签页
        self.key_management_tab = QWidget()
        self.create_key_management_tab()
        self.tab_widget.addTab(self.key_management_tab, "密钥管理")
        
        # 创建主布局
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.tab_widget)
        
        # 加载上次使用的数据库路径
        last_db_path = self.config.get("database_path", "")
        if last_db_path and os.path.exists(last_db_path):
            self.db_path_edit.setText(last_db_path)
    
    def create_login_tab(self):
        """创建登录标签页"""
        layout = QVBoxLayout(self.login_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("登录到密码库")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 数据库文件选择
        db_layout = QHBoxLayout()
        db_label = QLabel("数据库文件:")
        self.db_path_edit = QLineEdit()
        self.db_path_edit.setReadOnly(True)
        # 设置中文右键菜单
        self.db_path_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.db_path_edit.customContextMenuRequested.connect(self.show_context_menu)
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_database)
        db_layout.addWidget(db_label)
        db_layout.addWidget(self.db_path_edit)
        db_layout.addWidget(browse_button)
        layout.addLayout(db_layout)
        
        # 验证码输入
        auth_layout = QHBoxLayout()
        auth_label = QLabel("验证码:")
        self.auth_code_edit = QLineEdit()
        self.auth_code_edit.setMaxLength(6)
        self.auth_code_edit.setPlaceholderText("请输入 Authenticator 中的6位验证码")
        # 设置中文右键菜单
        self.auth_code_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.auth_code_edit.customContextMenuRequested.connect(self.show_context_menu)
        # 在验证码输入框按回车，直接触发登录
        self.auth_code_edit.returnPressed.connect(self.login)
        auth_layout.addWidget(auth_label)
        auth_layout.addWidget(self.auth_code_edit)
        layout.addLayout(auth_layout)
        
        # 登录按钮
        self.login_button = QPushButton("登录")
        self.login_button.setMinimumHeight(40)
        # 设置为默认按钮，支持全局回车触发
        self.login_button.setAutoDefault(True)
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)
        
        # 使用指南和功能介绍链接
        help_layout = QHBoxLayout()
        help_layout.addStretch()
        
        # 功能介绍按钮
        self.feature_button = QPushButton("🌟 功能介绍")
        self.feature_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #1976d2;
                border: none;
                text-decoration: underline;
                font-size: 16px;
                padding: 5px;
            }
            QPushButton:hover {
                color: #1565c0;
            }
        """)
        self.feature_button.clicked.connect(self.show_feature_guide)
        help_layout.addWidget(self.feature_button)
        
        # 分隔符
        separator = QLabel(" | ")
        separator.setStyleSheet("color: #666; font-size: 16px;")
        help_layout.addWidget(separator)
        
        # 快速入门按钮
        self.help_button = QPushButton("🚀 快速入门")
        self.help_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #1976d2;
                border: none;
                text-decoration: underline;
                font-size: 16px;
                padding: 5px;
            }
            QPushButton:hover {
                color: #1565c0;
            }
        """)
        self.help_button.clicked.connect(self.show_help_guide)
        help_layout.addWidget(self.help_button)
        
        help_layout.addStretch()
        layout.addLayout(help_layout)
        
        # 添加弹性空间
        layout.addStretch()
    
    def create_create_tab(self):
        """创建新建标签页"""
        # 修复拼写错误：creat -> create
        layout = QVBoxLayout(self.create_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("创建新的密码库")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 数据库文件选择
        db_layout = QHBoxLayout()
        db_label = QLabel("数据库文件:")
        self.new_db_path_edit = QLineEdit()
        self.new_db_path_edit.setReadOnly(True)
        # 设置中文右键菜单
        self.new_db_path_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.new_db_path_edit.customContextMenuRequested.connect(self.show_context_menu)
        new_browse_button = QPushButton("浏览...")
        new_browse_button.clicked.connect(self.browse_new_database)
        db_layout.addWidget(db_label)
        db_layout.addWidget(self.new_db_path_edit)
        db_layout.addWidget(new_browse_button)
        layout.addLayout(db_layout)
        
        # 用户名输入
        username_layout = QHBoxLayout()
        username_label = QLabel("用户名:")
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("输入用户名")
        # 设置中文右键菜单
        self.username_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.username_edit.customContextMenuRequested.connect(self.show_context_menu)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)
        layout.addLayout(username_layout)
        
        # 创建按钮
        self.create_button = QPushButton("创建")
        self.create_button.setMinimumHeight(40)
        self.create_button.clicked.connect(self.create_database)
        layout.addWidget(self.create_button)
        
        # QR码显示区域
        self.qr_group = QGroupBox("Authenticator设置")
        qr_layout = QVBoxLayout()
        
        self.qr_label = QLabel("创建数据库后将显示QR码")
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setMinimumSize(200, 200)
        qr_layout.addWidget(self.qr_label)
        
        self.secret_label = QLabel("")
        self.secret_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.secret_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        # 设置中文右键菜单
        self.secret_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.secret_label.customContextMenuRequested.connect(self.show_secret_label_context_menu)
        qr_layout.addWidget(self.secret_label)
        
        self.qr_group.setLayout(qr_layout)
        layout.addWidget(self.qr_group)
        
        # 添加弹性空间
        layout.addStretch()
    
    def create_settings_tab(self):
        """创建设置标签页"""
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 创建内容容器
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("应用程序设置")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setContentsMargins(0, 0, 0, 20)
        layout.addWidget(title_label)
        
        # 常规设置组
        general_group = QGroupBox("常规设置")
        general_group.setMinimumHeight(200)
        general_layout = QFormLayout()
        general_layout.setContentsMargins(10, 10, 10, 10)
        general_layout.setSpacing(8)
        general_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        general_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # 添加分隔空间
        layout.addSpacing(-25)
        
        # 主题选择
        theme_label = QLabel("主题:")
        theme_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色", "深色"])
        self.theme_combo.setCurrentIndex(0 if self.config.get("theme") == "light" else 1)
        self.theme_combo.setMinimumHeight(35)
        self.theme_combo.setMinimumWidth(150)
        self.theme_combo.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                font-size: 18px;
            }
        """)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        general_layout.addRow(theme_label, self.theme_combo)
        
        # 语言选择
        language_label = QLabel("语言:")
        language_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["简体中文", "English"])
        self.language_combo.setCurrentIndex(0 if self.config.get("language") == "zh_CN" else 1)
        self.language_combo.setMinimumHeight(35)
        self.language_combo.setMinimumWidth(150)
        self.language_combo.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                font-size: 18px;
            }
        """)
        general_layout.addRow(language_label, self.language_combo)
        
        # 自动锁定设置
        auto_lock_label = QLabel("自动锁定:")
        auto_lock_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.auto_lock_check = QCheckBox()
        self.auto_lock_check.setChecked(self.config.get("auto_lock", True))
        self.auto_lock_check.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        general_layout.addRow(auto_lock_label, self.auto_lock_check)
        
        # 锁定超时设置
        timeout_label = QLabel("锁定超时:")
        timeout_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.lock_timeout_spin = QSpinBox()
        self.lock_timeout_spin.setRange(1, 3600)
        self.lock_timeout_spin.setValue(self.config.get("lock_timeout", 300))
        self.lock_timeout_spin.setSuffix(" 秒")
        self.lock_timeout_spin.setMinimumHeight(35)
        self.lock_timeout_spin.setMinimumWidth(150)
        self.lock_timeout_spin.setStyleSheet("""
            QSpinBox {
                padding: 5px 10px;
                font-size: 18px;
            }
        """)
        general_layout.addRow(timeout_label, self.lock_timeout_spin)
        
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)
        
        # 备份设置组
        backup_group = QGroupBox("备份设置")
        backup_group.setMinimumHeight(200)
        backup_layout = QFormLayout()
        backup_layout.setContentsMargins(10, 10, 10, 10)
        backup_layout.setSpacing(8)
        backup_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        backup_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # 启用备份设置
        backup_enable_label = QLabel("启用自动备份:")
        backup_enable_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.backup_check = QCheckBox()
        self.backup_check.setChecked(self.config.get("backup_enabled", True))
        self.backup_check.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        backup_layout.addRow(backup_enable_label, self.backup_check)
        
        # 备份间隔设置
        interval_label = QLabel("备份间隔:")
        interval_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.backup_interval_spin = QSpinBox()
        self.backup_interval_spin.setRange(1, 30)
        self.backup_interval_spin.setValue(self.config.get("backup_interval", 7))
        self.backup_interval_spin.setSuffix(" 天")
        self.backup_interval_spin.setMinimumHeight(35)
        self.backup_interval_spin.setMinimumWidth(150)
        self.backup_interval_spin.setStyleSheet("""
            QSpinBox {
                padding: 5px 10px;
                font-size: 18px;
            }
        """)
        backup_layout.addRow(interval_label, self.backup_interval_spin)
        
        # 保留备份数量设置
        count_label = QLabel("保留备份数量:")
        count_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.backup_count_spin = QSpinBox()
        self.backup_count_spin.setRange(1, 20)
        self.backup_count_spin.setValue(self.config.get("backup_count", 5))
        self.backup_count_spin.setSuffix(" 个")
        self.backup_count_spin.setMinimumHeight(35)
        self.backup_count_spin.setMinimumWidth(150)
        self.backup_count_spin.setStyleSheet("""
            QSpinBox {
                padding: 5px 10px;
                font-size: 18px;
            }
        """)
        backup_layout.addRow(count_label, self.backup_count_spin)
        
        # 备份路径设置
        path_label = QLabel("备份路径:")
        path_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        backup_path_layout = QHBoxLayout()
        backup_path_layout.setSpacing(15)
        
        self.backup_path_edit = QLineEdit()
        self.backup_path_edit.setText(self.config.get("backup_path", ""))
        self.backup_path_edit.setReadOnly(True)
        self.backup_path_edit.setMinimumHeight(35)
        self.backup_path_edit.setStyleSheet("""
            QLineEdit {
                padding: 5px 10px;
                font-size: 18px;
                background-color: palette(base);
                color: palette(text);
            }
        """)
        # 设置中文右键菜单
        self.backup_path_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.backup_path_edit.customContextMenuRequested.connect(self.show_context_menu)
        
        backup_browse_button = QPushButton("浏览...")
        backup_browse_button.setMinimumHeight(35)
        backup_browse_button.setMinimumWidth(100)
        backup_browse_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 5px 15px;
            }
        """)
        backup_browse_button.clicked.connect(self.browse_backup_path)
        
        backup_path_layout.addWidget(self.backup_path_edit)
        backup_path_layout.addWidget(backup_browse_button)
        backup_layout.addRow(path_label, backup_path_layout)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # 添加分隔空间
        layout.addSpacing(10)
        
        # 保存按钮容器
        save_button_container = QHBoxLayout()
        save_button_container.setContentsMargins(0, 0, 0, 0)
        
        # 保存按钮
        self.save_settings_button = QPushButton("保存设置")
        self.save_settings_button.setMinimumHeight(45)
        self.save_settings_button.setMinimumWidth(220)
        self.save_settings_button.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 15px;
                padding: 8px 20px;
            }
        """)
        self.save_settings_button.clicked.connect(self.save_settings)
        
        # 将保存按钮添加到容器中并居中
        save_button_container.addStretch()
        save_button_container.addWidget(self.save_settings_button)
        save_button_container.addStretch()
        
        # 添加保存按钮容器
        layout.addLayout(save_button_container)
        
        # 添加底部空间
        layout.addSpacing(0)
        
        # 设置滚动区域的内容
        scroll_area.setWidget(content_widget)
        
        # 创建主布局并添加滚动区域
        main_layout = QVBoxLayout(self.settings_tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
    
    def browse_database(self):
        """浏览选择数据库文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择密码数据库文件", "", "密码数据库文件 (*.pwdb);;所有文件 (*.*)"
        )
        if file_path:
            self.db_path_edit.setText(file_path)
            # 切换数据库文件时，清除保存的TOTP密钥缓存
            # 这样可以避免使用上一个数据库的密钥
            if self.config.get("save_totp_key") and self.config.get("saved_totp_key"):
                # 询问用户是否清除保存的密钥
                reply = QMessageBox.question(
                    self, "清除密钥缓存", 
                    "检测到您选择了新的数据库文件。\n\n" +
                    "为避免使用错误的TOTP密钥，建议清除当前保存的密钥缓存。\n\n" +
                    "是否清除保存的TOTP密钥？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    # 清除保存的TOTP密钥配置
                    self.config.config["saved_totp_key"] = ""
                    self.config.config["save_totp_key"] = False
                    # 立即保存配置到文件
                    self.config.save()
                    # 清除Authenticator对象中的密钥缓存
                    if hasattr(self, 'authenticator'):
                        self.authenticator.secret = None
                        self.authenticator.totp = None
                    # 更新UI状态
                    if hasattr(self, 'save_key_check'):
                        self.save_key_check.setChecked(False)
                    QMessageBox.information(self, "成功", "已清除保存的TOTP密钥缓存！")
    
    def browse_new_database(self):
        """浏览选择新数据库文件保存位置"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存密码数据库文件", "", "密码数据库文件 (*.pwdb);;所有文件 (*.*)"
        )
        if file_path:
            # 确保文件扩展名为.pwdb
            if not file_path.endswith(".pwdb"):
                file_path += ".pwdb"
            self.new_db_path_edit.setText(file_path)
    
    def browse_backup_path(self):
        """浏览选择备份路径"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择备份目录", ""
        )
        if dir_path:
            self.backup_path_edit.setText(dir_path)
    
    def login(self):
        """登录到密码库"""
        db_path = self.db_path_edit.text()
        auth_code = self.auth_code_edit.text().strip()
        
        # 调试信息：显示路径相关信息
        print(f"=== 数据库路径调试信息 ===")
        print(f"用户选择的数据库路径: {db_path}")
        print(f"配置中的database_path: {self.config.get('database_path')}")
        print(f"get_effective_database_path(): {self.config.get_effective_database_path()}")
        print(f"云存储是否启用: {self.config.get_cloud_config('enabled')}")
        if self.config.get_cloud_config('enabled'):
            print(f"云存储类型: {self.config.get_cloud_config('type')}")
            print(f"网络驱动器路径: {self.config.get_cloud_config('network_drive_path')}")
            print(f"远程路径: {self.config.get_cloud_config('remote_path')}")
        print(f"=========================")
        
        # 修复：当用户选择新的数据库文件时，立即更新配置中的database_path
        # 这样可以确保get_effective_database_path()使用正确的文件名
        current_db_path = self.config.get('database_path')
        if current_db_path != db_path:
            print(f"检测到数据库路径变更，更新配置: {current_db_path} -> {db_path}")
            self.config.set('database_path', db_path)
            self.config.save()
            print(f"更新后的get_effective_database_path(): {self.config.get_effective_database_path()}")
        
        # 验证输入
        if not db_path:
            QMessageBox.warning(self, "错误", "请选择数据库文件")
            return
        
        if not os.path.exists(db_path):
            QMessageBox.warning(self, "错误", "数据库文件不存在")
            return
            
        if not auth_code:
            QMessageBox.warning(self, "错误", "请输入6位验证码")
            return
            
        if len(auth_code) != 6 or not auth_code.isdigit():
            QMessageBox.warning(self, "错误", "验证码必须是6位数字")
            return
        
        # 尝试打开数据库
        try:
            # 重新加载配置以确保获取最新的TOTP密钥状态
            self.config.load()
            # 首先尝试使用保存的TOTP密钥
            totp_key = self.config.get("saved_totp_key") if self.config.get("save_totp_key") else None
            
            # 如果没有保存的密钥，则要求用户输入
            if not totp_key:
                dialog = CustomInputDialog(self, "输入TOTP密钥", "请输入您的TOTP密钥（创建数据库时生成的base32编码字符串）:")
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    totp_key = dialog.get_text()
                else:
                    totp_key = None
                
                if not totp_key:
                    QMessageBox.warning(self, "错误", "请输入TOTP密钥")
                    return
            
            # 重新创建Authenticator实例以确保使用正确的密钥
            temp_authenticator = Authenticator(self.config)
            
            # 验证TOTP验证码
            if not temp_authenticator.verify_totp(totp_key, auth_code):
                # 检查是否使用了保存的TOTP密钥
                if self.config.get("save_totp_key") and self.config.get("saved_totp_key"):
                    error_msg = (
                        "验证码错误！\n\n"
                        "可能的原因：\n"
                        "1. 此设备保存了上一个数据库的TOTP密钥\n"
                        "2. 当前数据库使用了不同的TOTP密钥\n\n"
                        "解决方案：\n"
                        "• 请到'密钥管理'标签页清除保存的密钥\n"
                        "• 然后重新输入正确的TOTP密钥\n"
                        "• 或检查您的Authenticator应用中的验证码"
                    )
                else:
                    error_msg = "验证码错误，请检查您的Authenticator应用"
                
                QMessageBox.warning(self, "验证码错误", error_msg)
                return
            
            # 使用TOTP密钥打开数据库
            temp_db = PasswordDatabase(self.config)
            if not temp_db.open(db_path, str(totp_key)):
                # 根据错误类型显示不同的错误消息
                if hasattr(temp_db, 'last_error') and temp_db.last_error:
                    if temp_db.last_error == "FILE_NOT_FOUND":
                        error_msg = (
                            "数据库文件不存在！\n\n"
                            "可能的原因：\n"
                            "• 数据库文件已被删除或移动\n"
                            "• 云存储路径中的文件被清理\n"
                            "• 网络驱动器连接异常\n\n"
                            "解决方案：\n"
                            "• 检查文件路径是否正确\n"
                            "• 重新创建数据库或从备份恢复\n"
                            "• 检查云存储或网络连接"
                        )
                        QMessageBox.warning(self, "数据库文件不存在", error_msg)
                    elif temp_db.last_error == "INVALID_KEY":
                        # 检查是否使用了保存的TOTP密钥
                        if self.config.get("save_totp_key") and self.config.get("saved_totp_key"):
                            error_msg = (
                                "TOTP密钥错误！\n\n"
                                "可能的原因：\n"
                                "1. 此设备保存了上一个数据库的TOTP密钥\n"
                                "2. 当前数据库使用了不同的TOTP密钥\n\n"
                                "解决方案：\n"
                                "• 请到'密钥管理'标签页清除保存的密钥\n"
                                "• 然后重新输入正确的TOTP密钥\n"
                                "• 或检查您的Authenticator应用中的验证码"
                            )
                        else:
                            error_msg = "TOTP密钥错误，无法解密数据库\n\n请确保您输入的是正确的TOTP密钥"
                        QMessageBox.warning(self, "TOTP密钥错误", error_msg)
                    elif temp_db.last_error == "DATA_CORRUPTED":
                        error_msg = (
                            "数据库文件损坏！\n\n"
                            "数据库文件可能已损坏或格式不正确。\n\n"
                            "建议：\n"
                            "• 尝试从备份恢复数据库\n"
                            "• 检查文件是否完整\n"
                            "• 联系技术支持"
                        )
                        QMessageBox.warning(self, "数据库文件损坏", error_msg)
                    else:
                        error_msg = f"打开数据库失败：\n\n{temp_db.last_error_message or '未知错误'}"
                        QMessageBox.warning(self, "数据库错误", error_msg)
                else:
                    QMessageBox.warning(self, "错误", "无法打开数据库，请确保您输入的是正确的TOTP密钥")
                return
            
            # 我们已经打开了数据库，直接使用temp_db的数据
            self.db = temp_db
            
            # 保存数据库路径到配置
            self.config.set("database_path", db_path)
            
            # 如果用户选择记住TOTP密钥，则保存
            if not self.config.get("save_totp_key") and not self.config.get("saved_totp_key"):
                reply = QMessageBox.question(
                    self, "保存密钥", 
                    "是否保存TOTP密钥以便下次自动填入？\n（密钥将加密存储在本地配置中）",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.config.set("save_totp_key", True)
                    self.config.set("saved_totp_key", totp_key)
            
            # 清空验证码输入框
            self.auth_code_edit.clear()
            
            # 打开主窗口
            self.open_main_window()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"登录失败: {str(e)}")
    
    def create_database(self):
        """创建新的密码库"""
        db_path = self.new_db_path_edit.text()
        username = self.username_edit.text()
        
        # 验证输入
        if not db_path:
            QMessageBox.warning(self, "错误", "请选择数据库文件保存位置")
            return
        
        if not username:
            QMessageBox.warning(self, "错误", "请输入用户名")
            return
        
        # 检查文件是否已存在
        if os.path.exists(db_path):
            reply = QMessageBox.question(
                self, "确认", "文件已存在，是否覆盖？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        try:
            # 设置Authenticator
            secret = self.authenticator.setup(username)
            
            # 生成QR码
            qr_data = self.authenticator.get_qr_code(username)
            if qr_data:
                pixmap = QPixmap()
                pixmap.loadFromData(qr_data)
                self.qr_label.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
                self.secret_label.setText(f"密钥: {secret}")
            
            # 创建数据库（使用TOTP密钥作为主密码）
            QMessageBox.information(self, "重要提示", 
                                  "您的TOTP密钥已安全存储在数据库中。\n" + 
                                  "请确保您的手机上已安装Authenticator应用并扫描了QR码。\n" +
                                  "请使用Authenticator应用生成的验证码来打开数据库。")
            
            # 打印调试信息
            print(f"创建数据库使用的TOTP密钥: {secret}")
            
            if not self.db.create(db_path, str(secret), totp_secret=secret, username=username):
                QMessageBox.warning(self, "错误", "创建数据库失败")
                return
            
            # 保存数据库路径到配置
            self.config.set("database_path", db_path)
            
            # 获取实际的数据库文件位置
            actual_db_path = self.db.db_path if self.db.db_path else db_path
            
            # 显示成功消息，包含实际的数据库文件位置
            success_message = "数据库创建成功！\n\n"
            if actual_db_path != db_path:
                success_message += f"注意：由于云存储设置，数据库实际保存在：\n{actual_db_path}\n\n"
            else:
                success_message += f"数据库已保存到：\n{actual_db_path}\n\n"
            
            success_message += "⚠️ 重要提醒：\n" + \
                             "• TOTP密钥是解开数据库的唯一凭证！\n" + \
                             "• 请务必保存好您的TOTP密钥，建议多处备份\n" + \
                             "• 密钥丢失后将永远无法恢复数据库内容\n" + \
                             "• 请使用Authenticator应用扫描QR码或手动输入密钥\n" + \
                             "• 建议截图保存QR码作为备份"
            
            QMessageBox.information(self, "成功", success_message)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建数据库失败: {str(e)}")
    
    def apply_theme(self, theme):
        """应用主题"""
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow, QWidget { 
                    background-color: #2b2b2b; 
                    color: #ffffff; 
                    font-size: 16px;
                }
                QLabel { 
                    color: #ffffff; 
                    font-size: 16px;
                    padding: 2px;
                }
                QLineEdit, QSpinBox, QComboBox { 
                    background-color: #3b3b3b; 
                    color: #ffffff; 
                    border: 1px solid #555555;
                    padding: 8px;
                    font-size: 16px;
                    min-height: 20px;
                }
                QPushButton { 
                    background-color: #0d47a1; 
                    color: white; 
                    border: none; 
                    padding: 8px 15px;
                    border-radius: 4px;
                    font-size: 16px;
                    min-height: 20px;
                }
                QPushButton:hover { background-color: #1565c0; }
                QPushButton:pressed { background-color: #0a3d91; }
                QGroupBox { 
                    border: 1px solid #555555; 
                    color: #ffffff; 
                    margin-top: 15px; 
                    padding: 15px;
                    font-size: 16px;
                }
                QGroupBox::title { 
                    color: #ffffff; 
                    font-size: 18px;
                    font-weight: bold;
                    padding: 0 5px;
                }
                QCheckBox { 
                    color: #ffffff; 
                    font-size: 16px;
                    padding: 2px;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QTabWidget::pane {
                    border: 1px solid #555555;
                    background-color: #2b2b2b;
                }
                QTabBar::tab {
                    background-color: #3b3b3b;
                    color: #ffffff;
                    padding: 8px 15px;
                    font-size: 16px;
                    border: 1px solid #555555;
                    border-bottom: none;
                    min-width: 80px;
                }
                QTabBar::tab:selected {
                    background-color: #2b2b2b;
                    margin-bottom: -1px;
                }
                QTabBar::tab:!selected {
                    margin-top: 2px;
                }
            """)
        else:  # light theme
            self.setStyleSheet("""
                QMainWindow, QWidget { 
                    background-color: #ffffff; 
                    color: #000000; 
                    font-size: 16px;
                }
                QLabel { 
                    color: #000000; 
                    font-size: 16px;
                    padding: 2px;
                }
                QLineEdit, QSpinBox, QComboBox { 
                    background-color: #ffffff; 
                    color: #000000; 
                    border: 1px solid #cccccc;
                    padding: 8px;
                    font-size: 16px;
                    min-height: 20px;
                }
                QPushButton { 
                    background-color: #1976d2; 
                    color: white; 
                    border: none; 
                    padding: 8px 15px;
                    border-radius: 4px;
                    font-size: 16px;
                    min-height: 20px;
                }
                QPushButton:hover { background-color: #1e88e5; }
                QPushButton:pressed { background-color: #1565c0; }
                QGroupBox { 
                    border: 1px solid #cccccc; 
                    color: #000000; 
                    margin-top: 15px; 
                    padding: 15px;
                    font-size: 16px;
                }
                QGroupBox::title { 
                    color: #000000; 
                    font-size: 18px;
                    font-weight: bold;
                    padding: 0 5px;
                }
                QCheckBox {
                    color: #000000;
                    font-size: 16px;
                    padding: 2px;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
            """)

    def save_settings(self):
        """保存应用程序设置"""
        try:
            # 保存主题设置
            theme = "light" if self.theme_combo.currentIndex() == 0 else "dark"
            self.config.set("theme", theme)
            # 应用新主题
            self.apply_theme(theme)
            
            # 保存语言设置
            language = "zh_CN" if self.language_combo.currentIndex() == 0 else "en_US"
            self.config.set("language", language)
            
            # 保存自动锁定设置
            self.config.set("auto_lock", self.auto_lock_check.isChecked())
            self.config.set("lock_timeout", self.lock_timeout_spin.value())
            
            # 保存备份设置
            self.config.set("backup_enabled", self.backup_check.isChecked())
            self.config.set("backup_interval", self.backup_interval_spin.value())
            self.config.set("backup_count", self.backup_count_spin.value())
            self.config.set("backup_path", self.backup_path_edit.text())
            
            # 显示成功消息
            QMessageBox.information(self, "成功", "设置保存成功！")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}")
    
    def backup_totp_key(self):
        """备份TOTP密钥"""
        try:
            # 获取当前数据库的TOTP密钥
            db_path = self.db_path_edit.text()
            if not db_path or not os.path.exists(db_path):
                QMessageBox.warning(self, "错误", "请先选择数据库文件")
                return
            
            # 选择备份文件保存位置
            backup_path, _ = QFileDialog.getSaveFileName(
                self, "保存TOTP密钥备份", "", "TOTP密钥文件 (*.totp);;所有文件 (*.*)"
            )
            if not backup_path:
                return
                
            # 确保文件扩展名为.totp
            if not backup_path.endswith(".totp"):
                backup_path += ".totp"
            
            # 获取TOTP密钥
            totp_key = self.config.get("saved_totp_key")
            if not totp_key:
                dialog = CustomInputDialog(self, "输入TOTP密钥", "请输入要备份的TOTP密钥：")
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    totp_key = dialog.get_text()
                else:
                    totp_key = None
                
            if not totp_key:
                QMessageBox.warning(self, "错误", "请输入TOTP密钥")
                return
            
            # 保存密钥到文件
            with open(backup_path, "w") as f:
                f.write(totp_key)
            
            QMessageBox.information(self, "成功", "TOTP密钥已成功备份！")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"备份TOTP密钥失败: {str(e)}")
    
    def restore_totp_key(self):
        """恢复TOTP密钥"""
        try:
            # 选择备份文件
            backup_path, _ = QFileDialog.getOpenFileName(
                self, "选择TOTP密钥备份文件", "", "TOTP密钥文件 (*.totp);;所有文件 (*.*)"
            )
            if not backup_path:
                return
            
            # 读取密钥
            with open(backup_path, "r") as f:
                totp_key = f.read().strip()
            
            if not totp_key:
                QMessageBox.warning(self, "错误", "备份文件为空")
                return
            
            # 如果用户选择了保存密钥，则保存到配置中
            if self.save_key_check.isChecked():
                self.config.set("saved_totp_key", totp_key)
                self.config.set("save_totp_key", True)
            
            QMessageBox.information(
                self, "成功", 
                "TOTP密钥已成功恢复！\n" +
                ("密钥已保存到此设备" if self.save_key_check.isChecked() else "")
            )
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"恢复TOTP密钥失败: {str(e)}")
    
    def toggle_save_key(self, state):
        """切换是否保存TOTP密钥"""
        try:
            if state == Qt.CheckState.Checked.value:
                # 获取TOTP密钥
                dialog = CustomInputDialog(self, "输入TOTP密钥", "请输入要保存的TOTP密钥：")
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    totp_key = dialog.get_text()
                else:
                    totp_key = None
                
                if not totp_key:
                    self.save_key_check.setChecked(False)
                    return
                
                # 保存密钥到配置
                self.config.set("saved_totp_key", totp_key)
                self.config.set("save_totp_key", True)
                
                QMessageBox.information(self, "成功", "TOTP密钥已成功保存到此设备！")
            else:
                # 清除保存的密钥
                self.config.set("saved_totp_key", "")
                self.config.set("save_totp_key", False)
                
                # 清除Authenticator对象中的密钥缓存
                if hasattr(self, 'authenticator'):
                    self.authenticator.secret = None
                    self.authenticator.totp = None
                
                QMessageBox.information(self, "成功", "已清除保存的TOTP密钥！")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存TOTP密钥失败: {str(e)}")
            self.save_key_check.setChecked(False)
    
    def create_key_management_tab(self):
        """创建密钥管理标签页"""
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 创建内容容器
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("密钥管理")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setContentsMargins(0, 0, 0, 20)
        layout.addWidget(title_label)
        
        # 密钥备份和恢复组
        key_group = QGroupBox("密钥备份和恢复")
        key_group.setMinimumHeight(100)
        key_layout = QFormLayout()
        key_layout.setContentsMargins(10, 10, 10, 10)
        key_layout.setSpacing(8)
        key_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        key_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # 添加分隔空间
        layout.addSpacing(-30)

        # 密钥备份和恢复按钮布局
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # 密钥备份按钮
        self.backup_key_button = QPushButton("备份TOTP密钥")
        self.backup_key_button.setMinimumHeight(35)
        self.backup_key_button.setMinimumWidth(160)
        self.backup_key_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 5px 15px;
            }
        """)
        self.backup_key_button.clicked.connect(self.backup_totp_key)
        buttons_layout.addWidget(self.backup_key_button)
        
        # 密钥恢复按钮
        self.restore_key_button = QPushButton("恢复TOTP密钥")
        self.restore_key_button.setMinimumHeight(35)
        self.restore_key_button.setMinimumWidth(160)
        self.restore_key_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 5px 15px;
            }
        """)
        self.restore_key_button.clicked.connect(self.restore_totp_key)
        buttons_layout.addWidget(self.restore_key_button)
        
        key_layout.addRow(buttons_layout)
        
        # 添加间距
        key_layout.addItem(QSpacerItem(10, 10))
        
        # 密钥保存选项
        self.save_key_check = QCheckBox("在此设备上保存TOTP密钥")
        self.save_key_check.setStyleSheet("""
            QCheckBox {
                font-size: 18px;
                padding: 5px;
                spacing: 8px;
                color: red;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid palette(mid);
                border-radius: 4px;
                background-color: palette(base);
            }
            QCheckBox::indicator:hover {
                border-color: palette(highlight);
            }
            QCheckBox::indicator:checked {
                background-color: palette(highlight);
                border-color: palette(highlight);
                image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='20 6 9 17 4 12'%3E%3C/polyline%3E%3C/svg%3E");
                background-repeat: no-repeat;
                background-position: center;
            }
            QCheckBox::indicator:checked:hover {
                background-color: palette(highlight);
                border-color: palette(highlight);
                opacity: 0.8;
            }
        """)
        self.save_key_check.setChecked(self.config.get("save_totp_key", False))
        self.save_key_check.stateChanged.connect(self.toggle_save_key)
        key_layout.addRow(self.save_key_check)
        
        # 添加说明文本
        description_label = QLabel("保存TOTP密钥可以避免每次登录时手动输入密钥，但可能降低安全性。")
        description_label.setWordWrap(True)
        description_label.setStyleSheet("font-size: 18px; color: #FF0000;")
        key_layout.addRow(description_label)
        
    
        # 密钥说明
        key_info = QLabel(
            "TOTP密钥是打开密码库的唯一凭证，请务必妥善保管！\n\n" +
            "1. 在安全的设备上备份TOTP密钥\n\n" +
            "2. 将密钥打印出来保存在安全的地方\n\n" +
            "3. 定期验证备份的密钥是否可用"
        )
        key_info.setWordWrap(True)
        key_info.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: palette(base);
                color: palette(text);
                border-radius: 6px;
                font-size: 18px;
                line-height: 1.5;
            }
        """)
        key_layout.addRow(key_info)
        
        # 设置分组布局
        key_group.setLayout(key_layout)
        layout.addWidget(key_group)
        
        # 添加底部空间
        layout.addSpacing(0)
        
        # 设置滚动区域的内容
        scroll_area.setWidget(content_widget)
        
        # 创建主布局并添加滚动区域
        main_layout = QVBoxLayout(self.key_management_tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
    
    def on_theme_changed(self, index):
        """主题切换处理"""
        theme = "light" if index == 0 else "dark"
        self.config.set("theme", theme)
        self.apply_theme(theme)
    
    def open_main_window(self):
        """打开主窗口"""
        self.main_window = MainWindow(self.config, self.db, self.authenticator)
        self.main_window.show()
        self.hide()
    
    def show_help_guide(self):
        """显示快速入门"""
        import os
        import sys
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
        from PyQt6.QtCore import Qt
        
        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("快速入门")
        dialog.setMinimumSize(800, 600)
        dialog.setModal(True)
        
        # 创建布局
        layout = QVBoxLayout(dialog)
        
        # 创建文本显示区域
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        # 获取正确的文件路径
        try:
            # 获取应用程序的根目录
            if getattr(sys, 'frozen', False):
                # 如果是打包后的exe
                base_path = sys._MEIPASS
            else:
                # 如果是开发环境
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # 优先使用快速入门文档
            guide_file = os.path.join(base_path, "快速入门.md")
            
            # 如果快速入门文档不存在，则根据运行环境选择备用文档
            if not os.path.exists(guide_file):
                if os.name == 'nt':  # Windows
                    guide_file = os.path.join(base_path, "完整使用指南.md")
                else:  # Linux/Unix
                    guide_file = os.path.join(base_path, "UOS使用指南.md")
            
            if os.path.exists(guide_file):
                try:
                    with open(guide_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    text_edit.setMarkdown(content)
                except Exception as e:
                    text_edit.setPlainText(f"无法读取使用指南文件: {str(e)}")
            else:
                # 如果文件不存在，显示基本的快速入门说明
                basic_guide = """
# 密码管理工具 - 快速入门

## 🚀 5分钟快速上手

### 第一步：准备身份验证器
**⚠️ 重要：请先在手机上安装身份验证器应用！**

推荐：腾讯身份验证器（微信搜索小程序）、Google Authenticator

### 第二步：创建密码库
1. 切换到 **"新建"** 标签页
2. 选择数据库保存位置
3. 输入用户名，点击 **"创建"**
4. **立即用手机扫描QR码**
5. 保存密钥信息（重要备份！）

### 第三步：登录使用
1. 切换到 **"登录"** 标签页
2. 输入用户名和选择数据库文件
3. 输入手机验证器中的6位验证码
4. 点击 **"登录"** 进入主界面

## 📋 基本操作
- **添加密码**：点击工具栏"添加"按钮
- **使用密码**：双击查看，右键复制
- **搜索密码**：使用顶部搜索框

## 🔒 安全提醒
- ✅ 定期备份密码数据
- ✅ 保护好身份验证器密钥
- ✅ 不要在公共电脑上使用

---

**💡 提示**：快速入门文档未找到，显示基本说明。
文档路径：{guide_file}
""".format(guide_file=guide_file)
                text_edit.setMarkdown(basic_guide)
                
        except Exception as e:
            text_edit.setPlainText(f"加载使用指南时出错: {str(e)}")
        
        layout.addWidget(text_edit)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("关闭")
        close_button.clicked.connect(dialog.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # 显示对话框
        dialog.exec()
    
    def show_context_menu(self, pos):
        """显示中文右键菜单"""
        # 获取发送信号的输入框
        line_edit = self.sender()
        if not isinstance(line_edit, QLineEdit):
            return
        
        # 创建右键菜单
        context_menu = QMenu(self)
        
        # 撤销
        undo_action = context_menu.addAction("撤销")
        undo_action.setEnabled(line_edit.isUndoAvailable())
        undo_action.triggered.connect(line_edit.undo)
        
        # 重做
        redo_action = context_menu.addAction("重做")
        redo_action.setEnabled(line_edit.isRedoAvailable())
        redo_action.triggered.connect(line_edit.redo)
        
        context_menu.addSeparator()
        
        # 剪切
        cut_action = context_menu.addAction("剪切")
        cut_action.setEnabled(line_edit.hasSelectedText() and not line_edit.isReadOnly())
        cut_action.triggered.connect(line_edit.cut)
        
        # 复制
        copy_action = context_menu.addAction("复制")
        copy_action.setEnabled(line_edit.hasSelectedText())
        copy_action.triggered.connect(line_edit.copy)
        
        # 粘贴
        paste_action = context_menu.addAction("粘贴")
        paste_action.setEnabled(not line_edit.isReadOnly())
        paste_action.triggered.connect(line_edit.paste)
        
        # 删除
        delete_action = context_menu.addAction("删除")
        delete_action.setEnabled(line_edit.hasSelectedText() and not line_edit.isReadOnly())
        delete_action.triggered.connect(line_edit.clear)
        
        context_menu.addSeparator()
        
        # 全选
        select_all_action = context_menu.addAction("全选")
        select_all_action.setEnabled(len(line_edit.text()) > 0)
        select_all_action.triggered.connect(line_edit.selectAll)
        
        # 显示菜单
        context_menu.exec(line_edit.mapToGlobal(pos))
    
    def show_secret_label_context_menu(self, pos):
        """显示密钥标签的中文右键菜单"""
        label = self.sender()
        if not isinstance(label, QLabel):
            return
        
        # 创建右键菜单
        context_menu = QMenu(self)
        
        # 复制
        copy_action = context_menu.addAction("复制")
        copy_action.setEnabled(bool(label.selectedText()))
        copy_action.triggered.connect(lambda: self.copy_selected_text(label))
        
        # 全选
        select_all_action = context_menu.addAction("全选")
        select_all_action.triggered.connect(lambda: label.setSelection(0, len(label.text())))
        
        # 显示菜单
        context_menu.exec(label.mapToGlobal(pos))
    
    def copy_selected_text(self, label):
        """复制选中的文本"""
        import pyperclip
        selected_text = label.selectedText()
        if selected_text:
            pyperclip.copy(selected_text)
        else:
            # 如果没有选中文本，复制整个标签的文本
            pyperclip.copy(label.text())
    
    def show_feature_guide(self):
        """显示功能介绍"""
        import os
        import sys
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
        from PyQt6.QtCore import Qt
        
        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("功能介绍")
        dialog.setMinimumSize(800, 600)
        dialog.setModal(True)
        
        # 创建布局
        layout = QVBoxLayout(dialog)
        
        # 创建文本显示区域
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        # 获取正确的文件路径
        try:
            # 获取应用程序的根目录
            if getattr(sys, 'frozen', False):
                # 如果是打包后的exe
                base_path = sys._MEIPASS
            else:
                # 如果是开发环境
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # 功能介绍文件路径
            feature_file = os.path.join(base_path, "功能介绍.md")
            
            if os.path.exists(feature_file):
                try:
                    with open(feature_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    text_edit.setMarkdown(content)
                except Exception as e:
                    text_edit.setPlainText(f"无法读取功能介绍文件: {str(e)}")
            else:
                # 如果文件不存在，显示基本的功能介绍
                basic_feature = """
# 🔐 密码管理工具 - 您的数字生活安全卫士

## 🌟 为什么选择我们？

### 🛡️ 银行级安全保障
- 采用TOTP双因素认证，比传统密码更安全10倍
- 军用级AES加密算法，让黑客望而却步
- 自动锁定机制，离开电脑也不怕密码泄露

### 📱 极简操作体验
- 一键添加、编辑、删除密码，操作如丝般顺滑
- 智能分类管理，再多密码也井井有条
- 全局搜索功能，秒找目标密码
- 深色/浅色主题随心切换，护眼又美观

### ☁️ 多设备无缝同步
- 支持网络驱动器和云存储，多台电脑共享一个密码库
- 数据库文件轻松迁移，换电脑不丢数据
- 加密导出导入，安全备份无忧

### 🔄 智能备份系统
- 自动定时备份，再也不怕数据丢失
- 可配置备份间隔和保留数量，存储空间随你掌控
- 一键恢复功能，误删数据也能轻松找回

### 🎯 专为中国用户设计
- 完全中文界面，操作零门槛
- 支持腾讯身份验证器等国内主流应用
- 详细的使用指南和技术支持

## 💪 告别密码烦恼

### ❌ 过去的你：
- 用同一个密码到处注册，安全隐患巨大
- 密码太复杂记不住，太简单不安全
- 换手机后验证码收不到，账号找不回
- 重要密码忘记了，欲哭无泪

### ✅ 现在的你：
- 每个账号都有独特的强密码，安全无忧
- 一个主密码管理所有密码，简单高效
- TOTP验证码离线生成，不依赖手机号
- 自动备份保护，永远不怕数据丢失

## 🎁 立即体验

**💻 Windows用户**：下载exe文件，双击即用，无需安装  
**🐧 Linux用户**：支持统信UOS等国产操作系统  
**📖 新手友好**：内置详细使用指南，5分钟上手

---

**注意**：完整的功能介绍文档未找到。请确保安装包包含了完整的文档文件。
文档路径：{feature_file}
""".format(feature_file=feature_file)
                text_edit.setMarkdown(basic_feature)
                
        except Exception as e:
            text_edit.setPlainText(f"加载功能介绍时出错: {str(e)}")
        
        layout.addWidget(text_edit)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("关闭")
        close_button.clicked.connect(dialog.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # 显示对话框
        dialog.exec()