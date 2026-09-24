#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""定位题目行内嵌答案字母、内嵌正确/错误、无答案题目、单选项题目"""
import xml.etree.ElementTree as ET
import re

tree = ET.parse(r'D:\code\projects\Huawei\temp\word\document.xml')
root = tree.getroot()
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def para_text(para):
    text = ''
    for run in para.findall('.//w:r', ns):
        for t in run.findall('.//w:t', ns):
            if t.text:
                text += t.text
    return text.strip()


def para_highlights(para):
    hl = []
    for run in para.findall('.//w:r', ns):
        for rpr in run.findall('.//w:rPr', ns):
            for h in rpr.findall('.//w:highlight', ns):
                v = h.get(W + 'val')
                if v:
                    hl.append(v)
    return hl


paras = root.findall('.//w:p', ns)
lines = []
for p in paras:
    t = para_text(p)
    if t:
        lines.append((t, para_highlights(p)))

# 1. 题目行内嵌 E/F/G 选项字母的
print('--- 题目行中内嵌选项字母(E/F/G/H)的情况 ---')
for t, hl in lines:
    if re.match(r'^\d+', t):
        m = re.search(r'([E-H])[、.．:：]?\s*\S', t)
        if m:
            print(f'  {t[:110]} | HL={hl}')
            print()

# 2. 题目行末尾内嵌 正确/错误
print('--- 题目行末尾内嵌 正确/错误 ---')
for t, hl in lines:
    if re.match(r'^\d+', t) and re.search(r'(正确|错误)$', t):
        print(f'  {t[:110]} | HL={hl}')
        print()
