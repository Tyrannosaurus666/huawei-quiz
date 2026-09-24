#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深入分析特殊格式：判断题、超4选项题目、无选项题目、选项格式变体"""
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

# 找出所有'正确'/'错误'/'对'/'错'独立段落及其上下文
print('--- 判断类独立段落（正确/错误/对/错）---')
for i, (t, hl) in enumerate(lines):
    if t in ('正确', '错误', '对', '错', '正确。', '错误。'):
        # 打印前后文
        ctx_before = lines[i-3:i] if i >= 3 else lines[:i]
        ctx_after = lines[i+1:i+4]
        print(f'>>> 第{i}段: {t!r} HL={hl}')
        print('    前文:', [x[0][:50] for x in ctx_before])
        print('    后文:', [x[0][:50] for x in ctx_after])
        print()

print('--- 选项行格式统计（所有匹配 A/B/C/D/E/F/G 开头的行）---')
opt_patterns = {}
for t, hl in lines:
    m = re.match(r'^([A-H])[、.．:：]?\s*(.*)$', t)
    if m:
        letter = m.group(1)
        sep = t[1] if len(t) > 1 else ''
        key = f'{letter}{sep}'
        opt_patterns.setdefault(key, []).append((t, hl))

for k in sorted(opt_patterns.keys()):
    print(f'{k!r}: {len(opt_patterns[k])} 个，样例: {opt_patterns[k][0][0][:60]}')
