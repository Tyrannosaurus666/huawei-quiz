#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统计题目数量、题型分布，查看多选/判断的样例"""
import xml.etree.ElementTree as ET
import re
from collections import Counter

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

# 解析题目
questions = []
cur = None
cur_opts = []
cur_hl = []

for t, hl in lines:
    if re.match(r'^\d+[、.]', t) or re.match(r'^\d+\s*[、.]', t) or re.match(r'^\d+[^\d]', t):
        # 新题目
        if cur is not None and cur_opts:
            questions.append({'q': cur, 'opts': cur_opts, 'hl': cur_hl})
        cur = t
        cur_opts = []
        cur_hl = []
    elif re.match(r'^[A-D][、.．]', t):
        cur_opts.append(t)
        cur_hl.append('yellow' in hl)
    elif cur is not None:
        # 可能是题目续行
        cur += t

if cur is not None and cur_opts:
    questions.append({'q': cur, 'opts': cur_opts, 'hl': cur_hl})

print('题目总数:', len(questions))

# 按选项数量统计
opt_count = Counter(len(q['opts']) for q in questions)
print('按选项数量分布:', dict(sorted(opt_count.items())))

# 按答案数量统计
ans_count = Counter(sum(q['hl']) for q in questions)
print('按答案(黄色高亮)数量分布:', dict(sorted(ans_count.items())))

# 找出多选（多个黄色高亮）的题目
print('\n--- 多选题样例（答案数量>1）---')
shown = 0
for q in questions:
    if sum(q['hl']) > 1 and shown < 6:
        print(f"[{q['q'][:70]}]")
        for o, h in zip(q['opts'], q['hl']):
            print('   ', o[:70], '<== 答案' if h else '')
        print()
        shown += 1

# 找出只有2个选项的题目（可能是判断或AB型）
print('\n--- 2个选项的题目样例 ---')
shown = 0
for q in questions:
    if len(q['opts']) == 2 and shown < 6:
        print(f"[{q['q'][:70]}]")
        for o, h in zip(q['opts'], q['hl']):
            print('   ', o[:70], '<== 答案' if h else '')
        print()
        shown += 1

# 没有选项的题目
print('\n--- 无选项段落样例（前10个非题目非选项的段落）---')
shown = 0
for t, hl in lines:
    if not re.match(r'^\d+', t) and not re.match(r'^[A-D][、.．]', t) and shown < 10:
        print(repr(t[:90]), '| HL:', hl)
        shown += 1
