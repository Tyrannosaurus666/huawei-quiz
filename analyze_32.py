#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查看 32、 被拆分段落的完整上下文"""
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
lines = []
for p in paras:
    t = para_text(p)
    if t:
        lines.append((t, para_highlights(p)))

# [145] '32、' 附近
print('--- 段落 140-160 ---')
for j in range(140, 161):
    print(f'[{j}] {lines[j][0][:90]!r} | HL={lines[j][1]}')
