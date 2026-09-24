#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""index.html 静态自检"""
import re

html = open(r'D:\code\projects\Huawei\huawei-quiz-web\index.html', encoding='utf-8').read()

print('1. 占位符残留:', '__QUESTIONS_JSON__' in html)

local = re.findall(r'(?:src|href)="(?:file://|[A-Za-z]:[\\/]|/Users?/)', html)
print('2. 本地路径引用:', local if local else '无')

deps = re.findall(r'(?:src|href)="(https://[^"]+)"', html)
print('3. 外部依赖:')
for d in deps:
    print('   ', d[:110])

print('4. QUESTIONS 声明存在:', 'const QUESTIONS = ' in html)

print('5. 字体镜像 OK:', 'miaoda.feishu.cn/fonts/css2' in html)
banned = [k for k in ('googleapis', 'gstatic', 'bootcdn', 'staticfile', 'polyfill', 'unpkg') if k in html]
print('6. 禁止域名出现:', banned if banned else '无')

# 提取注入的 JSON 并验证可解析
m = re.search(r'const QUESTIONS = (\[.*?\]);', html, re.S)
if m:
    import json as _json
    try:
        data = _json.loads(m.group(1))
        print(f'7. 注入 JSON 可解析: OK, {len(data)} 题')
    except Exception as e:
        print('7. 注入 JSON 解析失败:', e)
else:
    print('7. 未找到 QUESTIONS 数组')

# 统计 JS 基本语法标记
print('8. script 标签配对:', html.count('<script>') == html.count('</script>'))
