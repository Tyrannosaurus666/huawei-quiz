#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""模拟用户输入测试 huawei_quiz.py"""
import subprocess
import sys

# 模拟输入：选择随机20题小测，答 1、2，然后退出(q)，回到菜单选 0 退出
test_input = '2\n1\n2\nq\n0\n'

p = subprocess.run(
    [sys.executable, r'D:\code\projects\Huawei\huawei_quiz.py'],
    input=test_input, capture_output=True, text=True, encoding='utf-8',
    timeout=60,
)
print(p.stdout)
if p.returncode != 0:
    print('STDERR:', p.stderr)
    print('退出码:', p.returncode)
else:
    print('程序正常退出，退出码 0')
