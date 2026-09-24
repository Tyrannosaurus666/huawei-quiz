#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
华为知识测验 - 题库解析器 v2
从 docx 提取题目，支持：单选题、多选题（A-H选项）、判断题（正确/错误）
答案依据：文档中黄色高亮标记
"""
import xml.etree.ElementTree as ET
import re
import json

DOCX_XML = r'D:\code\projects\Huawei\temp\word\document.xml'
OUT_JSON = r'D:\code\projects\Huawei\questions.json'

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def parse_docx_items():
    """返回 [(text, is_yellow), ...]，只含非空段落"""
    tree = ET.parse(DOCX_XML)
    root = tree.getroot()
    items = []
    for para in root.findall('.//w:p', NS):
        text = ''
        yellow = False
        for run in para.findall('.//w:r', NS):
            for rpr in run.findall('.//w:rPr', NS):
                for h in rpr.findall('.//w:highlight', NS):
                    if h.get(W + 'val') == 'yellow':
                        yellow = True
            for t in run.findall('.//w:t', NS):
                if t.text:
                    text += t.text
        text = text.strip()
        if text:
            items.append((text, yellow))
    return items


def is_judge_word(s):
    return s in ('正确', '错误')


def is_option_line(s):
    """形如 A.内容 / B、内容 / C内容 / D: 内容"""
    if len(s) < 2:
        return False
    return re.match(r'^[A-H][、.．:：]?\s*\S', s) is not None


def is_question_line(s):
    return re.match(r'^\d+', s) is not None


def parse_questions(items):
    questions = []
    i = 0
    n = len(items)
    stats = {'judge_standalone': 0, 'judge_embedded': 0,
             'embed_option_in_title': 0, 'merged_title_parts': 0}

    while i < n:
        text, yellow = items[i]

        if not is_question_line(text):
            i += 1
            continue

        # ===== 判断题：题目行末尾内嵌 正确/错误 =====
        if re.search(r'(正确|错误)$', text):
            answer = '正确' if text.endswith('正确') else '错误'
            qtext = re.sub(r'(正确|错误)$', '', text).rstrip('。.． ')
            questions.append({'type': 'judge', 'question': qtext, 'answer': answer})
            stats['judge_embedded'] += 1
            i += 1
            continue

        # ===== 处理题目行被拆分：题号行 + 正文行 =====
        if re.match(r'^\d+[、.．]?\s*$', text):
            if i + 1 < n and not is_question_line(items[i + 1][0]) \
                    and not is_option_line(items[i + 1][0]) \
                    and not is_judge_word(items[i + 1][0]):
                text += items[i + 1][0]
                yellow = yellow or items[i + 1][1]
                stats['merged_title_parts'] += 1
                i += 1

        # ===== 收集后续连续选项段落 =====
        j = i + 1
        opts = []
        seen_letters = set()
        while j < n and is_option_line(items[j][0]):
            m = re.match(r'^([A-H])[、.．:：]?\s*(.*)$', items[j][0])
            letter = m.group(1)
            content = m.group(2).strip()
            if letter not in seen_letters:
                opts.append({'letter': letter, 'content': content,
                             'answer': items[j][1]})
                seen_letters.add(letter)
            j += 1

        # ===== 判断题：无选项且下一段是 正确/错误 =====
        if not opts and j < n and is_judge_word(items[j][0]):
            questions.append({'type': 'judge', 'question': text,
                              'answer': items[j][0]})
            stats['judge_standalone'] += 1
            i = j + 1
            continue

        # ===== 内嵌选项剥离：题目行末尾 [A-H]内容 与独立选项一致才剥离 =====
        m = re.search(r'([A-H])[、.．:：]?\s*([^\s].*)$', text)
        if m:
            letter, content = m.group(1), m.group(2).strip()
            for o in opts:
                if o['letter'] == letter and o['content'] == content:
                    text = text[:m.start()].rstrip('。.．,， ')
                    stats['embed_option_in_title'] += 1
                    break

        if not opts:
            questions.append({'type': 'unknown', 'question': text,
                              'answer': None})
            i += 1
            continue

        answers = [o['letter'] for o in opts if o['answer']]
        questions.append({
            'type': 'choice',
            'question': text,
            'options': opts,
            'answer': ''.join(answers) if answers else None,
        })
        i = j

    return questions, stats


def main():
    items = parse_docx_items()
    questions, stats = parse_questions(items)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=1)

    print(f'题目总数: {len(questions)}')
    print(f'统计: {stats}')

    types = {}
    for q in questions:
        types.setdefault(q['type'], 0)
        types[q['type']] += 1
    print(f'题型分布: {types}')

    choice_types = {}
    for q in questions:
        if q['type'] == 'choice':
            key = f"{len(q['options'])}选项"
            choice_types.setdefault(key, 0)
            choice_types[key] += 1
    print(f'选择题选项数分布: {choice_types}')

    multi = sum(1 for q in questions if q['type'] == 'choice' and len(q['answer'] or '') > 1)
    single = sum(1 for q in questions if q['type'] == 'choice' and len(q['answer'] or '') == 1)
    print(f'选择题中: 单选 {single} 道, 多选 {multi} 道')

    no_ans = [q for q in questions if q['type'] == 'choice' and not q['answer']]
    print(f'\n无答案的选择题: {len(no_ans)}')
    for q in no_ans:
        print(f'  [{q["question"][:80]}] 选项: {[(o["letter"], o["content"][:25], o["answer"]) for o in q["options"]]}')

    bad = []
    for q in questions:
        if q['type'] == 'choice' and q['answer']:
            for a in q['answer']:
                if a not in [o['letter'] for o in q['options']]:
                    bad.append(q)
    print(f'\n答案字母超出选项范围的题: {len(bad)}')
    for q in bad:
        print(f'  [{q["question"][:80]}] 答案={q["answer"]} 选项={[o["letter"] for o in q["options"]]}')

    unk = [q for q in questions if q['type'] == 'unknown']
    print(f'\n异常题(无选项): {len(unk)}')
    for q in unk:
        print(f'  [{q["question"][:100]}]')


if __name__ == '__main__':
    main()
