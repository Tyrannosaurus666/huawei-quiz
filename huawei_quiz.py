#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
华为知识测验（驾考宝典版）
============================================
- 题库来源: questions.json（由 parse_questions.py 从 docx 解析生成）
- 题型: 单选题 / 多选题 / 判断题
- 答题: 用数字选择，单选 1-4 对应 ABCD，多选输入多个数字(如 13 或 1 3)，
        判断题 1=正确 2=错误
- 答完立即显示正确答案；支持随机练习、错题重练、得分统计
============================================
"""

import json
import os
import random
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'questions.json')


def setup_console():
    """Windows 控制台 UTF-8 编码适配"""
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            ctypes.windll.kernel32.SetConsoleCP(65001)
        except Exception:
            pass
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stdin.reconfigure(encoding='utf-8')
        except Exception:
            pass


def load_questions():
    with open(DATA_FILE, encoding='utf-8') as f:
        return json.load(f)


def type_label(q):
    if q['type'] == 'judge':
        return '判断题'
    if len(q.get('answer') or '') > 1:
        return '多选题'
    return '单选题'


def display_question(q, num, total):
    print('=' * 62)
    print(f'  第 {num}/{total} 题    [{type_label(q)}]')
    print('=' * 62)
    print(f'\n{q["question"]}\n')

    if q['type'] == 'choice':
        for idx, opt in enumerate(q['options'], 1):
            print(f'  {idx}. {opt["letter"]}. {opt["content"]}')
        print()
    else:
        print('  1. 正确')
        print('  2. 错误')
        print()


def get_answer(q):
    """获取用户答案，返回字母集合（判断题返回 {'正确'/'错误'}）"""
    if q['type'] == 'judge':
        while True:
            raw = input('  请选择 (1=正确, 2=错误): ').strip()
            if raw.lower() == 'q':
                return None
            if raw == '1':
                return {'正确'}
            if raw == '2':
                return {'错误'}
            print('  输入无效，请输入 1 或 2')
    else:
        n_opts = len(q['options'])
        hint = '多选' if len(q.get('answer') or '') > 1 else '单选'
        while True:
            raw = input(f'  请输入答案 (1-{n_opts}，{hint}，多个数字连写或空格分隔，如 1 3): ').strip()
            if raw.lower() == 'q':
                return None
            # 解析数字：连写(13)、空格(1 3)、逗号(1,3)均可
            if raw.isdigit():
                digits = [int(c) for c in raw] if len(raw) > 1 else [int(raw)]
            else:
                digits = [int(x) for x in re.split(r'[,\s]+', raw) if x.isdigit()]
            if not digits or any(d < 1 or d > n_opts for d in digits):
                print(f'  输入无效，请输入 1-{n_opts} 之间的数字')
                continue
            # 去重
            return {q['options'][d - 1]['letter'] for d in dict.fromkeys(digits)}


def re_split(raw):
    """把输入拆成数字片段：13 -> ['13']，1 3 -> ['1','3']，1,3 -> ['1','3']"""
    import re
    return re.findall(r'\d+', raw)


def check_answer(q, user_ans):
    if q['type'] == 'judge':
        correct = {q['answer']}
    else:
        correct = set(q['answer'])

    if user_ans == correct:
        print('\n  ✔ 回答正确！\n')
        return True
    else:
        print('\n  ✘ 回答错误！')
        if q['type'] == 'choice':
            ans_text = ' '.join(f'{o["letter"]}. {o["content"]}'
                                for o in q['options'] if o['letter'] in correct)
            print(f'  正确答案: {ans_text}')
        else:
            print(f'  正确答案: {q["answer"]}')
        print()
        return False


def run_practice(questions, title, max_num=None):
    """练习一轮，返回 (答对, 答错题列表)"""
    wrong = []
    correct_count = 0
    total = len(questions) if max_num is None else min(max_num, len(questions))

    print('\n' + '=' * 62)
    print(f'  {title}')
    print(f'  共 {total} 题，输入 q 随时退出')
    print('=' * 62)

    for i, q in enumerate(questions[:total], 1):
        display_question(q, i, total)
        user_ans = get_answer(q)
        if user_ans is None:
            print('\n  已退出本轮练习。')
            break
        if check_answer(q, user_ans):
            correct_count += 1
        else:
            wrong.append(q)
        if i < total:
            print('  ' + '-' * 58)
    else:
        pass

    done = i
    return correct_count, wrong, done


def main():
    setup_console()
    questions = load_questions()

    while True:
        print('\n' + '=' * 62)
        print('  华为服务知识测验  ·  驾考宝典版')
        print('  ' + '=' * 54)
        print('  题库: {} 题（单选 {} / 多选 {} / 判断 {}）'.format(
            len(questions),
            sum(1 for q in questions if q['type'] == 'choice' and len(q.get('answer') or '') == 1),
            sum(1 for q in questions if q['type'] == 'choice' and len(q.get('answer') or '') > 1),
            sum(1 for q in questions if q['type'] == 'judge'),
        ))
        print()
        print('  1. 随机练习（全题库随机顺序）')
        print('  2. 随机 20 题小测')
        print('  3. 只练选择题')
        print('  4. 只练判断题')
        print('  5. 错题重练')
        print('  0. 退出')
        print('=' * 62)

        choice = input('\n  请选择: ').strip()
        if choice == '0':
            print('  再见，加油！')
            break
        elif choice == '1':
            qs = questions[:]
            random.shuffle(qs)
            c, wrong, done = run_practice(qs, '随机练习 · 全题库')
        elif choice == '2':
            qs = questions[:]
            random.shuffle(qs)
            c, wrong, done = run_practice(qs, '随机 20 题小测', max_num=20)
        elif choice == '3':
            qs = [q for q in questions if q['type'] == 'choice']
            random.shuffle(qs)
            c, wrong, done = run_practice(qs, '选择题专项练习')
        elif choice == '4':
            qs = [q for q in questions if q['type'] == 'judge']
            random.shuffle(qs)
            c, wrong, done = run_practice(qs, '判断题专项练习')
        elif choice == '5':
            if not hasattr(main, 'wrong_book') or not main.wrong_book:
                print('\n  错题本还是空的，先去练习产生一些错题吧！')
                continue
            qs = main.wrong_book[:]
            random.shuffle(qs)
            c, wrong, done = run_practice(qs, '错题重练')
            main.wrong_book = wrong if wrong else []
        else:
            print('  无效选择，请重新输入')
            continue

        # 本轮成绩
        if done is not None:
            pct = c / done * 100
            print('=' * 62)
            print(f'  本轮成绩: 答对 {c}/{done} 题 ({pct:.1f}%)')
            if wrong and choice in ('1', '2', '3', '4'):
                print(f'  错题 {len(wrong)} 道已记入错题本，可随时选 5 重练')
                main.wrong_book = wrong
            print('=' * 62)


if __name__ == '__main__':
    main()
