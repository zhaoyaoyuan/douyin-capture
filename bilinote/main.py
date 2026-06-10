#!/usr/bin/env python3
"""
BiliNote Skill 入口脚本
当用户调用 /bilinote 时，此脚本将被执行
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate import main

if __name__ == '__main__':
    main()
