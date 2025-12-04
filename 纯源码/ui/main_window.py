#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主窗口模块
"""

import os
import sys
import pyperclip
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QTabWidget,
    QFormLayout, QGroupBox, QCheckBox, QSpinBox, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QDialog,
    QTextEdit, QSplitter, QTreeWidget, QTreeWidgetItem, QAbstractItemView,
    QToolBar, QStatusBar, QApplication, QInputDialog
)
from PyQt6.QtGui import QPixmap, QIcon, QFont, QAction, QKeySequence
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QEvent

# 添加云存储相关导入
try:
    from utils.cloud_sync import CloudSyncManager
    from ui.cloud_settings_dialog import CloudSettingsDialog
    CLOUD_SYNC_AVAILABLE = True
except ImportError:
    CLOUD_SYNC_AVAILABLE = False


class CustomInputDialog(QDialog):
    """自定义输入对话框，用于替代QInputDialog"""
    
    def __init__(self, parent=None, title="输入", label="请输入:", text=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setMinimumSize(300, 120)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标签
        label_widget = QLabel(label)
        layout.addWidget(label_widget)
        
        # 输入框
        self.line_edit = QLineEdit()
        self.line_edit.setText(text)
        self.line_edit.selectAll()
        # 设置中文右键菜单
        self.line_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.line_edit.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.line_edit)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        # 设置焦点
        self.line_edit.setFocus()
    
    def setFocus(self):
        """设置焦点到输入框"""
        self.line_edit.setFocus()
        self.line_edit.selectAll()
    
    def get_text(self):
        """获取输入的文本"""
        return self.line_edit.text()
    
    def show_context_menu(self, pos):
        """显示中文右键菜单"""
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


class PasswordDialog(QDialog):
    """密码对话框，用于添加或编辑密码"""
    
    def __init__(self, parent=None, categories=None, password_data=None):
        super().__init__(parent)
        
        self.categories = categories or []
        self.password_data = password_data or {}
        self.is_edit_mode = bool(password_data)
        
        self.setWindowTitle("编辑密码" if self.is_edit_mode else "添加密码")
        self.setMinimumSize(500, 400)
        
        # 获取父窗口的主题
        if parent and hasattr(parent, 'config'):
            theme = parent.config.get("theme", "light")
            self.apply_theme(theme)
        
        self.setup_ui()
        
        # 如果是编辑模式，填充数据
        if self.is_edit_mode:
            self.fill_form_data()
    
    def apply_theme(self, theme):
        """应用主题"""
        if theme == "dark":
            self.setStyleSheet("""
                QDialog, QWidget { 
                    background-color: #2b2b2b; 
                    color: #ffffff; 
                    font-size: 18px;
                }
                QLabel { 
                    color: #ffffff; 
                    font-size: 18px;
                    padding: 2px;
                }
                QLineEdit, QSpinBox, QComboBox, QTextEdit { 
                    background-color: #3b3b3b; 
                    color: #ffffff; 
                    border: 1px solid #555555;
                    padding: 8px;
                    font-size: 18px;
                    min-height: 20px;
                }
                QPushButton { 
                    background-color: #0d47a1; 
                    color: white; 
                    border: none; 
                    padding: 8px 15px;
                    border-radius: 4px;
                    font-size: 18px;
                    min-height: 20px;
                }
                QPushButton:hover { background-color: #1565c0; }
                QPushButton:pressed { background-color: #0a3d91; }
                QGroupBox { 
                    border: 1px solid #555555; 
                    color: #ffffff; 
                    margin-top: 15px; 
                    padding: 15px;
                    font-size: 18px;
                }
                QGroupBox::title { 
                    color: #ffffff; 
                    font-size: 19px;
                    font-weight: bold;
                    padding: 0 5px;
                }
            """)
        else:  # light theme
            self.setStyleSheet("""
                QDialog, QWidget { 
                    background-color: #ffffff; 
                    color: #000000; 
                    font-size: 18px;
                }
                QLabel { 
                    color: #000000; 
                    font-size: 18px;
                    padding: 2px;
                }
                QLineEdit, QSpinBox, QComboBox, QTextEdit { 
                    background-color: #ffffff; 
                    color: #000000; 
                    border: 1px solid #cccccc;
                    padding: 8px;
                    font-size: 18px;
                    min-height: 20px;
                }
                QPushButton { 
                    background-color: #1976d2; 
                    color: white; 
                    border: none; 
                    padding: 8px 15px;
                    border-radius: 4px;
                    font-size: 18px;
                    min-height: 20px;
                }
                QPushButton:hover { background-color: #1e88e5; }
                QPushButton:pressed { background-color: #1565c0; }
                QGroupBox { 
                    border: 1px solid #cccccc; 
                    color: #000000; 
                    margin-top: 15px; 
                    padding: 15px;
                    font-size: 18px;
                }
                QGroupBox::title { 
                    color: #000000; 
                    font-size: 19px;
                    font-weight: bold;
                    padding: 0 5px;
                }
            """)

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(15)
        
        # 标题
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("例如：GitHub账号")
        # 设置中文右键菜单
        self.title_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.title_edit.customContextMenuRequested.connect(self.show_password_dialog_context_menu)
        form_layout.addRow("标题:", self.title_edit)
        
        # 用户名
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("例如：user@example.com")
        # 设置中文右键菜单
        self.username_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.username_edit.customContextMenuRequested.connect(self.show_password_dialog_context_menu)
        username_layout = QHBoxLayout()
        username_layout.addWidget(self.username_edit)
        copy_username_btn = QPushButton("复制")
        copy_username_btn.setMaximumWidth(60)
        copy_username_btn.clicked.connect(lambda: pyperclip.copy(self.username_edit.text()))
        username_layout.addWidget(copy_username_btn)
        form_layout.addRow("用户名:", username_layout)
        
        # 密码
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("输入密码")
        # 设置中文右键菜单
        self.password_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.password_edit.customContextMenuRequested.connect(self.show_password_dialog_context_menu)
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_edit)
        self.show_password_btn = QPushButton("显示")
        self.show_password_btn.setMaximumWidth(60)
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.toggled.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.show_password_btn)
        copy_password_btn = QPushButton("复制")
        copy_password_btn.setMaximumWidth(60)
        copy_password_btn.clicked.connect(lambda: pyperclip.copy(self.password_edit.text()))
        password_layout.addWidget(copy_password_btn)
        form_layout.addRow("密码:", password_layout)
        
        # 网址
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("例如：https://github.com")
        # 设置中文右键菜单
        self.url_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.url_edit.customContextMenuRequested.connect(self.show_password_dialog_context_menu)
        form_layout.addRow("网址:", self.url_edit)
        
        # 分类
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.categories)
        form_layout.addRow("分类:", self.category_combo)
        
        # 备注
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("添加备注信息...")
        # 设置中文右键菜单
        self.notes_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.notes_edit.customContextMenuRequested.connect(self.show_password_dialog_context_menu)
        form_layout.addRow("备注:", self.notes_edit)
        
        layout.addLayout(form_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
    
    def toggle_password_visibility(self, checked):
        """切换密码可见性"""
        if checked:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("隐藏")
        else:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("显示")
    
    def fill_form_data(self):
        """填充表单数据"""
        self.title_edit.setText(self.password_data.get("title", ""))
        self.username_edit.setText(self.password_data.get("username", ""))
        self.password_edit.setText(self.password_data.get("password", ""))
        self.url_edit.setText(self.password_data.get("url", ""))
        
        # 设置分类
        category = self.password_data.get("category", "")
        index = self.category_combo.findText(category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        
        self.notes_edit.setText(self.password_data.get("notes", ""))
    
    def get_password_data(self):
        """获取密码数据"""
        data = {
            "title": self.title_edit.text(),
            "username": self.username_edit.text(),
            "password": self.password_edit.text(),
            "url": self.url_edit.text(),
            "category": self.category_combo.currentText(),
            "notes": self.notes_edit.toPlainText()
        }
        
        # 如果是编辑模式，保留原始ID
        if self.is_edit_mode and "id" in self.password_data:
            data["id"] = self.password_data["id"]
        
        return data
    
    def show_password_dialog_context_menu(self, pos):
        """显示密码对话框输入框的中文右键菜单"""
        sender = self.sender()
        menu = QMenu(self)
        
        # 区分输入控件类型
        is_line_edit = isinstance(sender, QLineEdit)
        is_text_edit = isinstance(sender, QTextEdit)
        has_selection = (
            sender.hasSelectedText() if is_line_edit else 
            (sender.textCursor().hasSelection() if is_text_edit else False)
        )
        is_read_only = sender.isReadOnly() if hasattr(sender, 'isReadOnly') else False
        can_paste = sender.canPaste() if hasattr(sender, 'canPaste') else True
        
        # 撤销
        undo_action = menu.addAction("撤销")
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(sender.undo)
        # QTextEdit 没有 isUndoAvailable；允许触发，由控件决定是否可撤销
        undo_action.setEnabled(
            sender.isUndoAvailable() if hasattr(sender, 'isUndoAvailable') else 
            (not is_read_only and is_text_edit)
        )
        
        # 重做
        redo_action = menu.addAction("重做")
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(sender.redo)
        redo_action.setEnabled(
            sender.isRedoAvailable() if hasattr(sender, 'isRedoAvailable') else 
            (not is_read_only and is_text_edit)
        )
        
        menu.addSeparator()
        
        # 剪切
        cut_action = menu.addAction("剪切")
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(sender.cut)
        cut_action.setEnabled(has_selection and not is_read_only)
        
        # 复制
        copy_action = menu.addAction("复制")
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(sender.copy)
        copy_action.setEnabled(has_selection)
        
        # 粘贴
        paste_action = menu.addAction("粘贴")
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(sender.paste)
        paste_action.setEnabled(not is_read_only and can_paste)
        
        # 删除
        delete_action = menu.addAction("删除")
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        def _delete_selected():
            if is_line_edit and sender.hasSelectedText():
                start = sender.selectionStart()
                selected = sender.selectedText()
                if start is not None and start >= 0 and selected:
                    text = sender.text()
                    end = start + len(selected)
                    sender.setText(text[:start] + text[end:])
                    sender.setCursorPosition(start)
            elif is_text_edit:
                cursor = sender.textCursor()
                if cursor and cursor.hasSelection():
                    cursor.removeSelectedText()
                    sender.setTextCursor(cursor)
        delete_action.triggered.connect(_delete_selected)
        delete_action.setEnabled(has_selection and not is_read_only)
        
        menu.addSeparator()
        
        # 全选
        select_all_action = menu.addAction("全选")
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(sender.selectAll)
        
        menu.exec(sender.mapToGlobal(pos))


class ExportImportDialog(QDialog):
    """导出导入对话框"""
    
    def __init__(self, parent=None, is_export=True):
        super().__init__(parent)
        
        self.is_export = is_export
        self.setWindowTitle("导出数据" if is_export else "导入数据")
        self.setMinimumSize(400, 200)
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 文件选择
        file_layout = QHBoxLayout()
        file_label = QLabel("文件路径:")
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        # 设置中文右键菜单
        self.file_path_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_path_edit.customContextMenuRequested.connect(self.show_export_import_context_menu)
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(browse_button)
        layout.addLayout(file_layout)
        
        # 密码输入
        password_layout = QHBoxLayout()
        password_label = QLabel("密码:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("输入用于加密/解密的密码")
        # 设置中文右键菜单
        self.password_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.password_edit.customContextMenuRequested.connect(self.show_export_import_context_menu)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)
        layout.addLayout(password_layout)
        
        # 确认密码（仅导出时显示）
        if self.is_export:
            confirm_layout = QHBoxLayout()
            confirm_label = QLabel("确认密码:")
            self.confirm_edit = QLineEdit()
            self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_edit.setPlaceholderText("再次输入密码")
            # 设置中文右键菜单
            self.confirm_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.confirm_edit.customContextMenuRequested.connect(self.show_export_import_context_menu)
            confirm_layout.addWidget(confirm_label)
            confirm_layout.addWidget(self.confirm_edit)
            layout.addLayout(confirm_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.ok_button = QPushButton("导出" if self.is_export else "导入")
        self.ok_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
    
    def browse_file(self):
        """浏览文件"""
        if self.is_export:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存导出文件", "", "加密数据文件 (*.pwex);;所有文件 (*.*)"
            )
            if file_path and not file_path.endswith(".pwex"):
                file_path += ".pwex"
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择导入文件", "", "加密数据文件 (*.pwex);;所有文件 (*.*)"
            )
        
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def validate_and_accept(self):
        """验证输入并接受"""
        file_path = self.file_path_edit.text()
        password = self.password_edit.text()
        
        if not file_path:
            QMessageBox.warning(self, "错误", "请选择文件路径")
            return
        
        if not password:
            QMessageBox.warning(self, "错误", "请输入密码")
            return
        
        if self.is_export:
            confirm = self.confirm_edit.text()
            if password != confirm:
                QMessageBox.warning(self, "错误", "两次输入的密码不一致")
                return
        
        self.accept()
    
    def get_data(self):
        """获取对话框数据"""
        return {
            "file_path": self.file_path_edit.text(),
            "password": self.password_edit.text()
        }
    
    def show_export_import_context_menu(self, pos):
        """显示导出导入对话框输入框的中文右键菜单"""
        sender = self.sender()
        menu = QMenu(self)
        
        # 撤销
        undo_action = menu.addAction("撤销")
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(sender.undo)
        undo_action.setEnabled(sender.isUndoAvailable() if hasattr(sender, 'isUndoAvailable') else False)
        
        # 重做
        redo_action = menu.addAction("重做")
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(sender.redo)
        redo_action.setEnabled(sender.isRedoAvailable() if hasattr(sender, 'isRedoAvailable') else False)
        
        menu.addSeparator()
        
        # 剪切
        cut_action = menu.addAction("剪切")
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(sender.cut)
        cut_action.setEnabled(sender.hasSelectedText() if hasattr(sender, 'hasSelectedText') else False)
        
        # 复制
        copy_action = menu.addAction("复制")
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(sender.copy)
        copy_action.setEnabled(sender.hasSelectedText() if hasattr(sender, 'hasSelectedText') else False)
        
        # 粘贴
        paste_action = menu.addAction("粘贴")
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(sender.paste)
        
        # 删除
        delete_action = menu.addAction("删除")
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        if hasattr(sender, 'hasSelectedText'):
            delete_action.triggered.connect(lambda: sender.del_() if sender.hasSelectedText() else None)
            delete_action.setEnabled(sender.hasSelectedText())
        else:
            delete_action.setEnabled(False)
        
        menu.addSeparator()
        
        # 全选
        select_all_action = menu.addAction("全选")
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(sender.selectAll)
        
        menu.exec(sender.mapToGlobal(pos))


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self, config, db, authenticator):
        super().__init__()
        
        self.config = config
        self.db = db
        self.authenticator = authenticator
        
        self.setWindowTitle("密码管理工具")
        self.setMinimumSize(1000, 700)  # 增加最小宽度以确保四个列都能显示
        
        # 初始化云存储相关变量
        self.cloud_sync_manager = None
        self.cloud_status_timer = None
        self.cloud_status_label = None
        
        # 应用主题
        self.apply_theme(self.config.get("theme", "light"))
        
        # 创建UI
        self.setup_ui()
        
        # 初始化云存储
        self.setup_cloud_sync()
        
        # 加载数据
        self.load_data()
        
        # 设置自动锁定定时器
        self.setup_auto_lock()
        
        # 设置事件过滤器（用于检测用户活动）
        self.installEventFilter(self)
        
        # 为主要控件安装事件过滤器
        self.install_event_filters()
        
        # 启动云状态更新定时器
        self.start_cloud_status_timer()
    
    def install_event_filters(self):
        """为主要控件安装事件过滤器"""
        # 为所有主要控件安装事件过滤器，确保用户活动能被检测到
        widgets_to_monitor = [
            self.search_edit,
            self.clear_search_button,
            self.category_tree,
            self.password_table,
            self.central_widget
        ]
        
        for widget in widgets_to_monitor:
            if widget:
                widget.installEventFilter(self)
    
    def apply_theme(self, theme):
        """应用主题"""
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow, QWidget { 
                    background-color: #2b2b2b; 
                    color: #ffffff; 
                    font-size: 18px;
                }
                QLabel { 
                    color: #ffffff; 
                    font-size: 18px;
                    padding: 2px;
                }
                QLineEdit, QSpinBox, QComboBox { 
                    background-color: #3b3b3b; 
                    color: #ffffff; 
                    border: 1px solid #555555;
                    padding: 8px;
                    font-size: 18px;
                    min-height: 20px;
                }
                QPushButton { 
                    background-color: #0d47a1; 
                    color: white; 
                    border: none; 
                    padding: 8px 15px;
                    border-radius: 4px;
                    font-size: 18px;
                    min-height: 20px;
                }
                QPushButton:hover { background-color: #1565c0; }
                QPushButton:pressed { background-color: #0a3d91; }
                QGroupBox { 
                    border: 1px solid #555555; 
                    color: #ffffff; 
                    margin-top: 15px; 
                    padding: 15px;
                    font-size: 18px;
                }
                QGroupBox::title { 
                    color: #ffffff; 
                    font-size: 19px;
                    font-weight: bold;
                    padding: 0 5px;
                }
                QCheckBox {
                    color: #ffffff;
                    font-size: 18px;
                    padding: 2px;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QTableWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    gridline-color: #555555;
                    border: 1px solid #555555;
                    font-size: 18px;
                }
                QTableWidget::item {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    padding: 5px;
                    min-height: 25px;
                }
                QTableWidget::item:selected {
                    background-color: #0d47a1;
                }
                QHeaderView {
                    background-color: #3b3b3b;
                    font-size: 18px;
                }
                QHeaderView::section {
                    background-color: #3b3b3b;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 5px;
                    font-size: 18px;
                    font-weight: bold;
                    min-height: 25px;
                }
                QScrollBar:vertical {
                    background-color: #2b2b2b;
                    border: 1px solid #555555;
                    width: 12px;
                }
                QScrollBar:horizontal {
                    background-color: #2b2b2b;
                    border: 1px solid #555555;
                    height: 12px;
                }
                QScrollBar::handle {
                    background-color: #3b3b3b;
                    min-height: 30px;
                    min-width: 30px;
                }
                QScrollBar::handle:hover {
                    background-color: #4b4b4b;
                }
                QScrollBar::add-line, QScrollBar::sub-line {
                    background-color: #2b2b2b;
                    height: 0px;
                    width: 0px;
                }
                QScrollBar::add-page, QScrollBar::sub-page {
                    background-color: #2b2b2b;
                }
            """)
        else:  # light theme
            self.setStyleSheet("""
                QMainWindow, QWidget { 
                    background-color: #ffffff; 
                    color: #000000; 
                    font-size: 18px;
                }
                QLabel { 
                    color: #000000; 
                    font-size: 18px;
                    padding: 2px;
                }
                QLineEdit, QSpinBox, QComboBox { 
                    background-color: #ffffff; 
                    color: #000000; 
                    border: 1px solid #cccccc;
                    padding: 8px;
                    font-size: 18px;
                    min-height: 20px;
                }
                QPushButton { 
                    background-color: #1976d2; 
                    color: white; 
                    border: none; 
                    padding: 8px 15px;
                    border-radius: 4px;
                    font-size: 18px;
                    min-height: 20px;
                }
                QPushButton:hover { background-color: #1e88e5; }
                QPushButton:pressed { background-color: #1565c0; }
                QGroupBox { 
                    border: 1px solid #cccccc; 
                    color: #000000; 
                    margin-top: 15px; 
                    padding: 15px;
                    font-size: 18px;
                }
                QGroupBox::title { 
                    color: #000000; 
                    font-size: 19px;
                    font-weight: bold;
                    padding: 0 5px;
                }
                QCheckBox {
                    color: #000000;
                    font-size: 18px;
                    padding: 2px;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QTableWidget {
                    background-color: #ffffff;
                    color: #000000;
                    gridline-color: #cccccc;
                    border: 1px solid #cccccc;
                    font-size: 18px;
                }
                QTableWidget::item {
                    background-color: #ffffff;
                    color: #000000;
                    padding: 5px;
                    min-height: 25px;
                }
                QTableWidget::item:selected {
                    background-color: #1976d2;
                    color: #ffffff;
                }
                QHeaderView {
                    background-color: #f5f5f5;
                    font-size: 18px;
                }
                QHeaderView::section {
                    background-color: #f5f5f5;
                    color: #000000;
                    border: 1px solid #cccccc;
                    padding: 5px;
                    font-size: 18px;
                    font-weight: bold;
                    min-height: 25px;
                }
                QScrollBar:vertical {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    width: 12px;
                }
                QScrollBar:horizontal {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    height: 12px;
                }
                QScrollBar::handle {
                    background-color: #f0f0f0;
                    min-height: 30px;
                    min-width: 30px;
                }
                QScrollBar::handle:hover {
                    background-color: #e0e0e0;
                }
                QScrollBar::add-line, QScrollBar::sub-line {
                    background-color: #ffffff;
                    height: 0px;
                    width: 0px;
                }
                QScrollBar::add-page, QScrollBar::sub-page {
                    background-color: #ffffff;
                }
            """)

    def setup_ui(self):
        """设置UI"""
        # 创建中心部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建搜索栏
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索密码...")
        self.search_edit.textChanged.connect(self.search_passwords)
        # 设置中文右键菜单
        self.search_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.search_edit.customContextMenuRequested.connect(self.show_search_context_menu)
        search_layout.addWidget(self.search_edit)
        
        self.clear_search_button = QPushButton("清除")
        self.clear_search_button.clicked.connect(self.clear_search)
        search_layout.addWidget(self.clear_search_button)
        
        main_layout.addLayout(search_layout)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 创建分类树
        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderLabel("分类")
        self.category_tree.setMinimumWidth(150)
        self.category_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.category_tree.customContextMenuRequested.connect(self.show_category_context_menu)
        self.category_tree.itemClicked.connect(self.category_selected)
        splitter.addWidget(self.category_tree)
        
        # 创建密码表格
        self.password_table = QTableWidget()
        self.password_table.setColumnCount(4)
        self.password_table.setHorizontalHeaderLabels(["标题", "用户名", "网址", "最后修改时间"])
        self.password_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        # 从配置文件加载列宽
        column_widths = self.config.get("column_widths", {
            "title": 180,
            "username": 150,
            "url": 180,
            "modified": 160
        })
        self.password_table.setColumnWidth(0, column_widths["title"])
        self.password_table.setColumnWidth(1, column_widths["username"])
        self.password_table.setColumnWidth(2, column_widths["url"])
        self.password_table.setColumnWidth(3, column_widths["modified"])
        
        # 设置表格最小宽度，确保所有列都能显示
        min_table_width = sum(column_widths.values()) + 50  # 额外50像素用于边距和滚动条
        self.password_table.setMinimumWidth(min_table_width)
        
        # 连接列宽改变信号
        self.password_table.horizontalHeader().sectionResized.connect(self.on_column_resized)
        
        self.password_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.password_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.password_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.password_table.customContextMenuRequested.connect(self.show_password_context_menu)
        self.password_table.doubleClicked.connect(self.edit_password)
        splitter.addWidget(self.password_table)
        
        # 设置分割器比例，增加表格区域的宽度
        splitter.setSizes([200, 800])
        main_layout.addWidget(splitter)
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # 创建云存储状态标签（如果云存储可用）
        if CLOUD_SYNC_AVAILABLE:
            self.cloud_status_label = QLabel("云存储: 未启用")
            self.cloud_status_label.setStyleSheet("QLabel { padding: 0 10px; }")
            self.statusBar.addPermanentWidget(self.cloud_status_label)
        
        # 创建右侧永久标签用于显示倒计时
        self.lock_timer_label = QLabel("自动锁定: 03:00")
        self.lock_timer_label.setStyleSheet("QLabel { padding: 0 10px; }")
        self.statusBar.addPermanentWidget(self.lock_timer_label)
        
        # 左侧显示基本状态信息
        self.statusBar.showMessage("就绪")
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # 添加密码
        add_action = QAction("添加密码", self)
        add_action.setShortcut(QKeySequence("Ctrl+N"))
        add_action.triggered.connect(self.add_password)
        toolbar.addAction(add_action)
        
        # 编辑密码
        edit_action = QAction("编辑密码", self)
        edit_action.setShortcut(QKeySequence("Ctrl+E"))
        edit_action.triggered.connect(self.edit_password)
        toolbar.addAction(edit_action)
        
        # 删除密码
        delete_action = QAction("删除密码", self)
        delete_action.setShortcut(QKeySequence("Delete"))
        delete_action.triggered.connect(self.delete_password)
        toolbar.addAction(delete_action)
        
        toolbar.addSeparator()
        
        # 添加分类
        add_category_action = QAction("添加分类", self)
        add_category_action.triggered.connect(self.add_category)
        toolbar.addAction(add_category_action)
        
        toolbar.addSeparator()
        
        # 导出数据
        export_action = QAction("导出数据", self)
        export_action.triggered.connect(self.export_data)
        toolbar.addAction(export_action)
        
        # 导入数据
        import_action = QAction("导入数据", self)
        import_action.triggered.connect(self.import_data)
        toolbar.addAction(import_action)
        
        toolbar.addSeparator()
        
        # 云存储功能（如果可用）
        if CLOUD_SYNC_AVAILABLE:
            # 手动同步
            manual_sync_action = QAction("手动同步", self)
            manual_sync_action.setShortcut(QKeySequence("Ctrl+S"))
            manual_sync_action.triggered.connect(self.manual_sync)
            toolbar.addAction(manual_sync_action)
            
            # 云存储设置
            cloud_settings_action = QAction("云存储设置", self)
            cloud_settings_action.triggered.connect(self.open_cloud_settings)
            toolbar.addAction(cloud_settings_action)
            
            toolbar.addSeparator()
        
        # 锁定
        lock_action = QAction("锁定", self)
        lock_action.setShortcut(QKeySequence("Ctrl+L"))
        lock_action.triggered.connect(self.lock)
        toolbar.addAction(lock_action)
        
        toolbar.addSeparator()
        
        # 指南
        guide_action = QAction("使用指南", self)
        guide_action.triggered.connect(self.show_guide)
        toolbar.addAction(guide_action)
    
    def show_guide(self):
        """显示指南对话框"""
        guide_dialog = QDialog(self)
        guide_dialog.setWindowTitle("使用指南")
        guide_dialog.setMinimumSize(800, 600)
        
        # 创建布局
        layout = QVBoxLayout(guide_dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # 创建导航栏
        nav_layout = QHBoxLayout()
        
        # 文档选择下拉框
        doc_selector = QComboBox()
        
        # 根据运行环境和可用文档选择默认文档
        import os
        import sys
        
        # 获取应用程序的根目录
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 检查可用的文档文件并添加到下拉框
        available_docs = []
        
        # 定义文档文件映射
        doc_files = {
            "UOS使用指南": "UOS使用指南.md",
            "完整使用指南": "完整使用指南.md", 
            "README": "README.md",
            "云存储同步指南": "云存储同步指南.md",
        }
        
        # 检查文件是否存在并添加到可用列表
        for display_name, filename in doc_files.items():
            file_path = os.path.join(base_path, filename)
            if os.path.exists(file_path):
                doc_selector.addItem(display_name, filename)
                available_docs.append((display_name, filename))
        
        # 如果没有找到任何文档，添加一个默认项
        if not available_docs:
            doc_selector.addItem("基本使用说明", "basic_guide")
        
        # 根据运行环境选择默认文档
        if os.name == 'nt':  # Windows
            default_doc = "完整使用指南.md"
        else:  # Linux/Unix
            default_doc = "UOS使用指南.md"
        
        # 设置默认选中项
        for i in range(doc_selector.count()):
            if doc_selector.itemData(i) == default_doc:
                doc_selector.setCurrentIndex(i)
                break
        
        nav_layout.addWidget(QLabel("选择文档："))
        nav_layout.addWidget(doc_selector)
        nav_layout.addStretch()
        
        layout.addLayout(nav_layout)
        
        # 创建文本编辑器并设置为只读
        guide_text = QTextEdit()
        guide_text.setReadOnly(True)
        
        # 设置样式
        guide_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
                font-size: 14px;
                line-height: 1.6;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        
        layout.addWidget(guide_text)
        
        # 文档加载函数
        def load_document(filename):
            try:
                if filename == "basic_guide":
                    # 显示基本使用说明
                    basic_content = """
# 密码管理工具 - 基本使用指南

## 🚀 快速开始

### 首次使用
1. **创建密码库**：
   - 切换到"新建"标签页
   - 选择数据库文件保存位置
   - 输入用户名并点击"创建"
   - 使用手机上的身份验证器应用扫描显示的QR码
   - 保存好密钥信息（重要！）

2. **登录验证**：
   - 切换到"登录"标签页
   - 输入用户名
   - 选择对应的数据库文件
   - 输入身份验证器应用中显示的6位验证码
   - 点击"登录"

## 📋 主要功能

### 密码管理
- **添加密码**：点击工具栏"添加"按钮，填写密码信息
- **编辑密码**：双击密码条目或选中后点击"编辑"
- **删除密码**：选中密码后点击"删除"按钮
- **复制密码**：右键点击密码条目，选择复制选项

### 分类管理
- **创建分类**：在左侧分类树中右键，选择"添加分类"
- **筛选查看**：点击左侧分类查看对应密码
- **搜索功能**：使用顶部搜索框快速查找密码

### 数据安全
- **自动备份**：程序会自动创建数据备份
- **数据加密**：所有密码数据都经过加密存储
- **TOTP认证**：使用时间动态密码保障安全

## 💡 安全建议
- 定期备份密码数据
- 保护好Authenticator密钥
- 使用强密码保护重要账号
- 定期更新系统和应用程序

---

**注意**：这是基本使用说明。完整的文档文件未找到，请检查安装包是否包含完整的文档文件。
"""
                    guide_text.setMarkdown(basic_content)
                    return
                
                file_path = os.path.join(base_path, filename)
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    # 处理内部链接，将.md链接转换为提示文本
                    import re
                    
                    # 替换.md文件链接为提示文本
                    def replace_md_links(match):
                        link_text = match.group(1)
                        link_url = match.group(2)
                        if link_url.endswith('.md'):
                            return f"**{link_text}** (请在上方下拉框中选择对应文档)"
                        return match.group(0)
                    
                    # 处理Markdown链接格式 [文本](链接)
                    content = re.sub(r'\[([^\]]+)\]\(([^)]+\.md[^)]*)\)', replace_md_links, content)
                    
                    guide_text.setMarkdown(content)
                    
                except FileNotFoundError:
                    guide_text.setPlainText(f"未找到文档文件：{filename}\n文件路径：{file_path}")
                    
            except Exception as e:
                guide_text.setPlainText(f"无法加载文档内容: {str(e)}")
        
        # 文档选择变化事件
        def on_doc_changed():
            current_data = doc_selector.currentData()
            if current_data:
                load_document(current_data)
        
        doc_selector.currentTextChanged.connect(on_doc_changed)
        
        # 默认加载第一个可用文档
        if doc_selector.count() > 0:
            load_document(doc_selector.currentData())
        
        # 添加关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(guide_dialog.close)
        close_button.setMaximumWidth(100)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        guide_dialog.exec()
    
    def load_data(self):
        """加载数据"""
        # 加载分类
        self.load_categories()
        
        # 加载所有密码
        self.load_passwords()
    
    def load_categories(self):
        """加载分类"""
        self.category_tree.clear()
        
        # 添加"全部"分类
        all_item = QTreeWidgetItem(self.category_tree)
        all_item.setText(0, "全部")
        all_item.setData(0, Qt.ItemDataRole.UserRole, "all")
        
        # 添加数据库中的分类
        categories = self.db.get_categories()
        for category in categories:
            item = QTreeWidgetItem(self.category_tree)
            item.setText(0, category)
            item.setData(0, Qt.ItemDataRole.UserRole, category)
        
        # 默认选中"全部"分类
        self.category_tree.setCurrentItem(all_item)
    
    def load_passwords(self, category=None, search_query=None):
        """加载密码"""
        self.password_table.setRowCount(0)
        
        # 获取密码列表
        if search_query:
            passwords = self.db.search_passwords(search_query)
        elif category and category != "all":
            passwords = self.db.get_passwords_by_category(category)
        else:
            passwords = self.db.get_all_passwords()
        
        # 填充表格
        for i, pwd in enumerate(passwords):
            self.password_table.insertRow(i)
            
            # 标题
            title_item = QTableWidgetItem(pwd.get("title", ""))
            title_item.setData(Qt.ItemDataRole.UserRole, pwd.get("id"))
            self.password_table.setItem(i, 0, title_item)
            
            # 用户名
            username_item = QTableWidgetItem(pwd.get("username", ""))
            self.password_table.setItem(i, 1, username_item)
            
            # 网址
            url_item = QTableWidgetItem(pwd.get("url", ""))
            self.password_table.setItem(i, 2, url_item)
            
            # 最后修改时间
            updated_at = pwd.get("updated_at", "")
            if updated_at:
                try:
                    dt = datetime.fromisoformat(updated_at)
                    updated_at = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            time_item = QTableWidgetItem(updated_at)
            self.password_table.setItem(i, 3, time_item)
        
        # 在状态栏左侧显示密码总数
        self.statusBar.showMessage(f"共 {len(passwords)} 个密码")
    
    def show_temporary_message(self, message, duration=3000):
        """显示临时消息，指定时间后恢复显示密码总数"""
        # 显示临时消息
        self.statusBar.showMessage(message)
        
        # 创建定时器，在指定时间后恢复显示密码总数
        QTimer.singleShot(duration, self.restore_password_count_display)
    
    def restore_password_count_display(self):
        """恢复显示密码总数"""
        # 获取当前密码总数并显示
        current_item = self.category_tree.currentItem()
        if current_item:
            category = current_item.data(0, Qt.ItemDataRole.UserRole)
            if category == "all":
                passwords = self.db.get_all_passwords()
            else:
                passwords = self.db.get_passwords_by_category(category)
            self.statusBar.showMessage(f"共 {len(passwords)} 个密码")
    
    def category_selected(self, item):
        """分类选择事件"""
        category = item.data(0, Qt.ItemDataRole.UserRole)
        self.load_passwords(category)
        self.search_edit.clear()
    
    def search_passwords(self):
        """搜索密码"""
        query = self.search_edit.text()
        if query:
            self.load_passwords(search_query=query)
        else:
            # 如果搜索框为空，显示当前选中的分类
            current_item = self.category_tree.currentItem()
            if current_item:
                category = current_item.data(0, Qt.ItemDataRole.UserRole)
                self.load_passwords(category)
    
    def clear_search(self):
        """清除搜索"""
        self.search_edit.clear()
        current_item = self.category_tree.currentItem()
        if current_item:
            category = current_item.data(0, Qt.ItemDataRole.UserRole)
            self.load_passwords(category)
    
    def add_password(self):
        """添加密码"""
        dialog = PasswordDialog(self, self.db.get_categories())
        # 应用当前主题
        dialog.apply_theme(self.config.get("theme", "light"))
        if dialog.exec():
            password_data = dialog.get_password_data()
            if self.db.add_password(password_data):
                # 刷新密码列表
                current_item = self.category_tree.currentItem()
                if current_item:
                    category = current_item.data(0, Qt.ItemDataRole.UserRole)
                    self.load_passwords(category)
                # 密码添加成功的消息会在load_passwords中更新密码总数时显示
            else:
                QMessageBox.warning(self, "错误", "添加密码失败")
    
    def edit_password(self):
        """编辑密码"""
        selected_items = self.password_table.selectedItems()
        if not selected_items:
            return
        
        # 获取密码ID
        row = selected_items[0].row()
        password_id = self.password_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # 获取密码数据
        password_data = self.db.get_password(password_id)
        if not password_data:
            return
        
        # 打开编辑对话框
        dialog = PasswordDialog(self, self.db.get_categories(), password_data)
        # 应用当前主题
        dialog.apply_theme(self.config.get("theme", "light"))
        if dialog.exec():
            updated_data = dialog.get_password_data()
            if self.db.update_password(password_id, updated_data):
                # 刷新密码列表
                current_item = self.category_tree.currentItem()
                if current_item:
                    category = current_item.data(0, Qt.ItemDataRole.UserRole)
                    self.load_passwords(category)
                # 密码更新成功的消息会在load_passwords中更新密码总数时显示
            else:
                QMessageBox.warning(self, "错误", "更新密码失败")
    
    def delete_password(self):
        """删除密码"""
        selected_items = self.password_table.selectedItems()
        if not selected_items:
            return
        
        # 获取密码ID
        row = selected_items[0].row()
        title = self.password_table.item(row, 0).text()
        password_id = self.password_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除密码 \"{title}\" 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_password(password_id):
                # 刷新密码列表
                current_item = self.category_tree.currentItem()
                if current_item:
                    category = current_item.data(0, Qt.ItemDataRole.UserRole)
                    self.load_passwords(category)
                # 密码删除成功的消息会在load_passwords中更新密码总数时显示
            else:
                QMessageBox.warning(self, "错误", "删除密码失败")
    
    def add_category(self):
        """添加分类"""
        dialog = CustomInputDialog(self, "添加分类", "请输入分类名称:")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            category = dialog.get_text()
        else:
            category = None
        if category:
            if category in self.db.get_categories():
                QMessageBox.warning(self, "错误", "分类已存在")
                return
            
            if self.db.add_category(category):
                self.load_categories()
                # 重新加载当前密码列表以更新状态栏的密码总数
                current_item = self.category_tree.currentItem()
                if current_item:
                    current_category = current_item.data(0, Qt.ItemDataRole.UserRole)
                    self.load_passwords(current_category)
            else:
                QMessageBox.warning(self, "错误", "添加分类失败")
    
    def rename_category(self):
        """修改分类名称"""
        current_item = self.category_tree.currentItem()
        if not current_item:
            return
        
        old_category = current_item.data(0, Qt.ItemDataRole.UserRole)
        if old_category == "all":
            QMessageBox.warning(self, "错误", "无法修改\"全部\"分类")
            return
        
        # 输入新的分类名称
        dialog = CustomInputDialog(self, "修改分类名称", f"请输入新的分类名称：", old_category)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_category = dialog.get_text()
        else:
            new_category = None
        
        if new_category and new_category.strip():
            new_category = new_category.strip()
            
            # 检查新名称是否与现有分类重复
            if new_category == old_category:
                return  # 名称没有变化
            
            if new_category in self.db.get_categories():
                QMessageBox.warning(self, "错误", f"分类 \"{new_category}\" 已存在")
                return
            
            # 执行重命名
            if self.db.rename_category(old_category, new_category):
                self.load_categories()
                # 重新选择修改后的分类
                self.select_category(new_category)
            else:
                QMessageBox.warning(self, "错误", "修改分类名称失败")
    
    def select_category(self, category_name):
        """选择指定的分类"""
        for i in range(self.category_tree.topLevelItemCount()):
            item = self.category_tree.topLevelItem(i)
            if item.data(0, Qt.ItemDataRole.UserRole) == category_name:
                self.category_tree.setCurrentItem(item)
                self.load_passwords(category_name)
                break
    
    def delete_category(self):
        """删除分类"""
        current_item = self.category_tree.currentItem()
        if not current_item:
            return
        
        category = current_item.data(0, Qt.ItemDataRole.UserRole)
        if category == "all":
            QMessageBox.warning(self, "错误", "无法删除\"全部\"分类")
            return
        
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除分类 \"{category}\" 吗？\n\n注意：该分类下的密码将被移动到\"其他\"分类。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_category(category):
                self.load_categories()
                self.load_passwords()
            else:
                QMessageBox.warning(self, "错误", "删除分类失败")
    
    def export_data(self):
        """导出数据"""
        dialog = ExportImportDialog(self, is_export=True)
        if dialog.exec():
            data = dialog.get_data()
            if self.db.export_data(data["file_path"], data["password"]):
                QMessageBox.information(self, "成功", "数据导出成功")
            else:
                QMessageBox.warning(self, "错误", "数据导出失败")
    
    def import_data(self):
        """导入数据"""
        dialog = ExportImportDialog(self, is_export=False)
        if dialog.exec():
            data = dialog.get_data()
            if self.db.import_data(data["file_path"], data["password"]):
                QMessageBox.information(self, "成功", "数据导入成功")
                self.load_categories()
                self.load_passwords()
            else:
                QMessageBox.warning(self, "错误", "数据导入失败")
    
    def show_password_context_menu(self, pos):
        """显示密码上下文菜单"""
        selected_items = self.password_table.selectedItems()
        if not selected_items:
            return
        
        # 创建上下文菜单
        context_menu = QMenu(self)
        
        # 复制用户名
        copy_username_action = context_menu.addAction("复制用户名")
        
        # 复制密码
        copy_password_action = context_menu.addAction("复制密码")
        
        # 编辑密码
        edit_action = context_menu.addAction("编辑")
        
        # 删除密码
        delete_action = context_menu.addAction("删除")
        
        # 显示菜单并处理选择
        action = context_menu.exec(self.password_table.mapToGlobal(pos))
        
        if not action:
            return
        
        # 获取密码ID
        row = selected_items[0].row()
        password_id = self.password_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        password_data = self.db.get_password(password_id)
        
        if action == copy_username_action:
            pyperclip.copy(password_data.get("username", ""))
            self.show_temporary_message("用户名已复制到剪贴板")
        
        elif action == copy_password_action:
            pyperclip.copy(password_data.get("password", ""))
            self.show_temporary_message("密码已复制到剪贴板")
        
        elif action == edit_action:
            self.edit_password()
        
        elif action == delete_action:
            self.delete_password()
    
    def show_category_context_menu(self, pos):
        """显示分类上下文菜单"""
        current_item = self.category_tree.currentItem()
        if not current_item:
            return
        
        category = current_item.data(0, Qt.ItemDataRole.UserRole)
        if category == "all":
            return
        
        # 创建上下文菜单
        context_menu = QMenu(self)
        
        # 修改分类名称
        rename_action = context_menu.addAction("修改分类名称")
        
        # 删除分类
        delete_action = context_menu.addAction("删除分类")
        
        # 显示菜单并处理选择
        action = context_menu.exec(self.category_tree.mapToGlobal(pos))
        
        if action == rename_action:
            self.rename_category()
        elif action == delete_action:
            self.delete_category()
    
    def show_search_context_menu(self, pos):
        """显示搜索框中文右键菜单"""
        line_edit = self.search_edit
        
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
        cut_action.setEnabled(line_edit.hasSelectedText())
        cut_action.triggered.connect(line_edit.cut)
        
        # 复制
        copy_action = context_menu.addAction("复制")
        copy_action.setEnabled(line_edit.hasSelectedText())
        copy_action.triggered.connect(line_edit.copy)
        
        # 粘贴
        paste_action = context_menu.addAction("粘贴")
        paste_action.triggered.connect(line_edit.paste)
        
        # 删除
        delete_action = context_menu.addAction("删除")
        delete_action.setEnabled(line_edit.hasSelectedText())
        delete_action.triggered.connect(line_edit.clear)
        
        context_menu.addSeparator()
        
        # 全选
        select_all_action = context_menu.addAction("全选")
        select_all_action.setEnabled(len(line_edit.text()) > 0)
        select_all_action.triggered.connect(line_edit.selectAll)
        
        # 显示菜单
        context_menu.exec(line_edit.mapToGlobal(pos))
    
    def setup_auto_lock(self):
        """设置自动锁定"""
        self.auto_lock_enabled = self.config.get("auto_lock", True)
        self.lock_timeout = self.config.get("lock_timeout", 300)  # 保持秒为单位
        
        # 初始化最后活动时间为当前时间
        self.last_activity_time = datetime.now()
        
        # 创建定时器
        self.lock_timer = QTimer(self)
        self.lock_timer.timeout.connect(self.check_auto_lock)
        self.lock_timer.start(1000)  # 每1秒检查一次，提高响应性
    
    def check_auto_lock(self):
        """检查是否需要自动锁定"""
        if not self.auto_lock_enabled:
            # 如果自动锁定未启用，隐藏倒计时标签
            self.lock_timer_label.setText("自动锁定: 已禁用")
            return
        
        # 计算不活动时间（秒）
        inactive_time = (datetime.now() - self.last_activity_time).total_seconds()
        
        # 计算剩余时间
        remaining_time = self.lock_timeout - inactive_time
        
        # 在右侧标签显示倒计时
        if remaining_time > 0:
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            self.lock_timer_label.setText(f"自动锁定倒计时: {minutes:02d}:{seconds:02d}")
        else:
            self.lock_timer_label.setText("自动锁定倒计时: 00:00")
        
        # 如果不活动时间超过设定的锁定时间，则锁定
        if inactive_time >= self.lock_timeout:
            self.lock()
    
    def eventFilter(self, obj, event):
        """事件过滤器，用于检测用户活动"""
        # 检测各种用户活动事件
        activity_events = [
            QEvent.Type.MouseButtonPress,
            QEvent.Type.MouseButtonRelease,
            QEvent.Type.KeyPress,
            QEvent.Type.KeyRelease,
            QEvent.Type.Wheel,
            QEvent.Type.FocusIn,
            QEvent.Type.WindowActivate
        ]
        
        # 对于鼠标移动，只在移动距离较大时才认为是活动
        if event.type() == QEvent.Type.MouseMove:
            if hasattr(self, '_last_mouse_pos'):
                current_pos = event.globalPosition() if hasattr(event, 'globalPosition') else event.globalPos()
                if hasattr(current_pos, 'toPoint'):
                    current_pos = current_pos.toPoint()
                
                # 计算移动距离
                distance = ((current_pos.x() - self._last_mouse_pos.x()) ** 2 + 
                           (current_pos.y() - self._last_mouse_pos.y()) ** 2) ** 0.5
                
                # 只有移动距离大于10像素时才更新活动时间
                if distance > 10:
                    self.last_activity_time = datetime.now()
                    self._last_mouse_pos = current_pos
            else:
                # 第一次记录鼠标位置
                current_pos = event.globalPosition() if hasattr(event, 'globalPosition') else event.globalPos()
                if hasattr(current_pos, 'toPoint'):
                    current_pos = current_pos.toPoint()
                self._last_mouse_pos = current_pos
                self.last_activity_time = datetime.now()
        
        elif event.type() in activity_events:
            # 更新最后活动时间
            self.last_activity_time = datetime.now()
        
        return super().eventFilter(obj, event)
    
    def lock(self):
        """锁定应用程序"""
        # 停止自动锁定定时器
        if hasattr(self, 'lock_timer'):
            self.lock_timer.stop()
        
        # 关闭主窗口，返回登录窗口
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow(self.config)
        self.login_window.show()
        self.close()
    
    def on_column_resized(self, column, old_width, new_width):
        """列宽改变事件处理"""
        # 保存列宽到配置
        column_widths = self.config.get("column_widths", {})
        column_map = {0: "title", 1: "username", 2: "url", 3: "modified"}
        if column in column_map:
            column_widths[column_map[column]] = new_width
            self.config.set("column_widths", column_widths)
    
    def closeEvent(self, event):
        """关闭事件处理"""
        # 停止云状态更新定时器
        if self.cloud_status_timer:
            self.cloud_status_timer.stop()
        
        # 停止云同步
        if self.cloud_sync_manager:
            self.cloud_sync_manager.stop_auto_sync()
        
        # 保存配置
        self.config.save()
        event.accept()
    
    # 云存储相关方法
    def setup_cloud_sync(self):
        """初始化云存储同步"""
        if not CLOUD_SYNC_AVAILABLE:
            print("云存储功能不可用")
            return
        
        try:
            self.cloud_sync_manager = CloudSyncManager(self.config)
            print("云存储管理器初始化成功")
        except Exception as e:
            print(f"云存储初始化失败: {e}")
            import traceback
            traceback.print_exc()
            self.cloud_sync_manager = None
    
    def start_cloud_status_timer(self):
        """启动云状态更新定时器"""
        if not CLOUD_SYNC_AVAILABLE or not self.cloud_status_label:
            return
        
        self.cloud_status_timer = QTimer(self)
        self.cloud_status_timer.timeout.connect(self.update_cloud_status)
        self.cloud_status_timer.start(5000)  # 每5秒更新一次状态
        
        # 立即更新一次状态
        self.update_cloud_status()
    
    def update_cloud_status(self):
        """更新云存储状态显示"""
        if not CLOUD_SYNC_AVAILABLE or not self.cloud_status_label:
            if self.cloud_status_label:
                self.cloud_status_label.setText("云存储: 功能不可用")
                self.cloud_status_label.setStyleSheet("QLabel { padding: 0 10px; color: gray; }")
            return
        
        if not self.cloud_sync_manager:
            self.cloud_status_label.setText("云存储: 功能未初始化")
            self.cloud_status_label.setStyleSheet("QLabel { padding: 0 10px; color: gray; }")
            return
        
        try:
            # 获取同步状态字符串
            status_text = self.cloud_sync_manager.get_sync_status()
            
            if not self.cloud_sync_manager.is_cloud_enabled():
                self.cloud_status_label.setText("云存储: 未启用")
                self.cloud_status_label.setStyleSheet("QLabel { padding: 0 10px; color: gray; }")
            elif self.cloud_sync_manager.is_syncing:
                self.cloud_status_label.setText("云存储: 同步中...")
                self.cloud_status_label.setStyleSheet("QLabel { padding: 0 10px; color: orange; }")
            elif "未同步" in status_text:
                self.cloud_status_label.setText("云存储: 未同步")
                self.cloud_status_label.setStyleSheet("QLabel { padding: 0 10px; color: gray; }")
            elif "最后同步" in status_text:
                self.cloud_status_label.setText(f"云存储: {status_text}")
                self.cloud_status_label.setStyleSheet("QLabel { padding: 0 10px; color: green; }")
            else:
                self.cloud_status_label.setText(f"云存储: {status_text}")
                self.cloud_status_label.setStyleSheet("QLabel { padding: 0 10px; color: red; }")
                
        except Exception as e:
            self.cloud_status_label.setText("云存储: 状态获取失败")
            self.cloud_status_label.setStyleSheet("QLabel { padding: 0 10px; color: red; }")
            print(f"云存储状态更新失败: {e}")
    
    def manual_sync(self):
        """手动同步"""
        if not CLOUD_SYNC_AVAILABLE or not self.cloud_sync_manager:
            QMessageBox.warning(self, "错误", "云存储功能不可用")
            return
        
        if not self.cloud_sync_manager.is_cloud_enabled():
            QMessageBox.information(self, "提示", "云存储未启用，请先在设置中启用云存储功能")
            return
        
        try:
            # 显示同步进度
            self.statusBar.showMessage("正在进行手动同步...")
            
            # 执行同步
            success, message = self.cloud_sync_manager.manual_sync()
            
            if success:
                QMessageBox.information(self, "成功", "手动同步完成")
                self.statusBar.showMessage("手动同步完成", 3000)
            else:
                QMessageBox.warning(self, "同步失败", f"手动同步失败: {message}")
                self.statusBar.showMessage("手动同步失败", 3000)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"手动同步时发生错误: {str(e)}")
            self.statusBar.showMessage("手动同步错误", 3000)
        
        # 立即更新状态
        self.update_cloud_status()
    
    def open_cloud_settings(self):
        """打开云存储设置对话框"""
        if not CLOUD_SYNC_AVAILABLE:
            QMessageBox.warning(self, "错误", "云存储功能不可用")
            return
        
        try:
            dialog = CloudSettingsDialog(self, self.config)
            if dialog.exec():
                # 设置已保存，重新初始化云同步
                self.setup_cloud_sync()
                self.update_cloud_status()
                QMessageBox.information(self, "成功", "云存储设置已保存并重新初始化")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开云存储设置时发生错误: {str(e)}")