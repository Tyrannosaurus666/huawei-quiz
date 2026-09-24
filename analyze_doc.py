#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分析 docx 文档结构，摸清题目、选项、答案格式"""
import xml.etree.ElementTree as ET

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
print('总段落数:', len(paras))

# 收集所有非空段落，含高亮信息
lines = []
for p in paras:
    t = para_text(p)
    if t:
        lines.append((t, para_highlights(p)))

print('非空段落数:', len(lines))
print('--- 前60个非空段落 ---')
for i, (l, hl) in enumerate(lines[:60]):
    print(i, repr(l[:90]), '| HL:', hl)
