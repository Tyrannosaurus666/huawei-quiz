#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查看题目被拆分的原始段落上下文"""
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

print('--- 找 "61、使用手机查询门店" 和 "32、" 相关段落 ---')
for i, (t, hl) in enumerate(lines):
    if t.startswith('61、使用手机查询门店') or t == '32、' or t.startswith('32、') or t.startswith('PP更新至最新版') or t.startswith('61、'):
        print(f'[{i}] {t[:110]!r} | HL={hl}')
        print()
