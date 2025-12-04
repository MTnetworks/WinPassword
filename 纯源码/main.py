#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
密码管理工具主程序
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTranslator, QLocale

from ui.login_window import LoginWindow
from utils.config import Config


def main():
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 设置应用程序图标
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe
        base_path = sys._MEIPASS
    else:
        # 如果是开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    icon_path = os.path.join(base_path, "resources", "icons", "app_icon.svg")
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)
    
    # 加载配置
    config = Config()
    config.load()
    
    # 创建并显示登录窗口
    login_window = LoginWindow(config)
    login_window.show()
    
    # 运行应用程序主循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()