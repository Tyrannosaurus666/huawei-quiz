#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建驾考宝典前端页面：把 questions.json 注入 template.html 生成 index.html"""
import json
import os

BASE = r'D:\code\projects\Huawei'
SRC = os.path.join(BASE, 'huawei-quiz-web', 'template.html')
OUT = os.path.join(BASE, 'huawei-quiz-web', 'index.html')
DATA = os.path.join(BASE, 'questions.json')


def js_json(data):
    """json.dumps 后转义 script 内不安全的字符"""
    s = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    s = s.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    s = s.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    return s


def main():
    with open(DATA, encoding='utf-8') as f:
        questions = json.load(f)
    with open(SRC, encoding='utf-8') as f:
        html = f.read()

    payload = js_json(questions)
    html = html.replace('__QUESTIONS_JSON__', payload)

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)

    print('题目数:', len(questions))
    print('输出:', OUT)
    print('文件大小: %.1f KB' % (os.path.getsize(OUT) / 1024))


if __name__ == '__main__':
    main()
