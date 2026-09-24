#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查看特定题目的完整上下文 + 找出无答案/单选项的异常题"""
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

# 查看含 'E.常见服务' / 'E.产品百科信息' / 'B产品参数' 的题目上下文
print('=== 内嵌选项字母题目的上下文 ===')
for i, (t, hl) in enumerate(lines):
    if ('E.常见服务' in t or 'E.产品百科信息' in t or 'B产品参数' in t or 'E.升级' in t):
        print(f'--- 第{i}段 ---')
        for j in range(max(0, i - 4), min(len(lines), i + 8)):
            print(f'  [{j}] {lines[j][0][:80]} | HL={lines[j][1]}')
        print()

# 完整解析，找出无答案/单选项的题
print('=== 异常题目（无选项/单选项/无答案）===')
questions = []
cur = None
cur_opts = []
cur_hl = []
for t, hl in lines:
    if re.match(r'^\d+', t):
        if cur is not None and cur_opts:
            questions.append({'q': cur, 'opts': cur_opts, 'hl': cur_hl})
        cur = t
        cur_opts = []
        cur_hl = []
    elif re.match(r'^[A-H][、.．:：]?\s*\S', t):
        cur_opts.append(t)
        cur_hl.append('yellow' in hl)
    elif cur is not None:
        cur += t

if cur is not None and cur_opts:
    questions.append({'q': cur, 'opts': cur_opts, 'hl': cur_hl})

for i, q in enumerate(questions):
    n_ans = sum(q['hl'])
    if len(q['opts']) <= 1 or n_ans == 0:
        print(f'[{i}] 题目: {q["q"][:90]}')
        print(f'     选项({len(q["opts"])}): {q["opts"]}')
        print(f'     高亮: {q["hl"]}')
        print()
