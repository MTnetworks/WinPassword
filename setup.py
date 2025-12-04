#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="password-manager",
    version="1.0.0",
    description="密码管理工具",
    long_description="一个基于PyQt6的现代化密码管理工具",
    author="Password Manager Team",
    author_email="admin@example.com",
    url="https://github.com/example/password-manager",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyQt6>=6.0.0",
        "pyotp>=2.8.0",
        "cryptography>=41.0.0",
        "pillow>=10.0.0",
        "qrcode>=7.4.2",
        "pyperclip>=1.8.2",
    ],
    entry_points={
        'console_scripts': [
            'password-manager=main:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
)