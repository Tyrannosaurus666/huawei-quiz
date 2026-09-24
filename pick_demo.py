#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""随机抽一道4选项单选题用于演示"""
import json
import random

qs = json.load(open(r'D:\code\projects\Huawei\questions.json', encoding='utf-8'))
cands = [q for q in qs
         if q['type'] == 'choice' and len(q['options']) == 4
         and len(q.get('answer') or '') == 1]
q = random.choice(cands)
print('QUESTION:', q['question'])
for i, o in enumerate(q['options'], 1):
    print(f"{i}. {o['letter']}. {o['content']}")
print('ANSWER:', q['answer'])
