#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
华为知识测验程序 - 类似驾考宝典
从docx XML中提取题目，随机出题，支持1234选择答案
"""

import xml.etree.ElementTree as ET
import random
import re
import os
import sys

# 设置控制台编码
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


def parse_questions_from_xml(xml_file):
    """解析XML文件，提取题目、选项和答案"""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # 命名空间
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

    questions = []
    current_question = None
    current_options = []
    current_answer = None

    # 遍历所有段落
    for para in root.findall(".//w:p", ns):
        # 获取段落文本
        text = ""
        for run in para.findall(".//w:r", ns):
            for t in run.findall(".//w:t", ns):
                if t.text:
                    text += t.text

        text = text.strip()
        if not text:
            continue

        # 检查是否是题目（以数字开头，后面跟着"、"或"."）
        if re.match(r"^\d+[、.]", text):
            # 保存前一道题
            if current_question and current_options:
                questions.append(
                    {
                        "question": current_question,
                        "options": current_options,
                        "answer": current_answer,
                    }
                )

            # 开始新题目
            current_question = text
            current_options = []
            current_answer = None

        # 检查是否是选项（A. B. C. D.）
        elif re.match(r"^[A-D][.]", text):
            # 检查是否有黄色高亮
            is_answer = False
            for run in para.findall(".//w:r", ns):
                for rpr in run.findall(".//w:rPr", ns):
                    for highlight in rpr.findall(".//w:highlight", ns):
                        if (
                            highlight.get(
                                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
                            )
                            == "yellow"
                        ):
                            is_answer = True

            current_options.append(text)
            if is_answer:
                # 提取选项字母
                current_answer = text[0]  # A, B, C, or D

    # 保存最后一道题
    if current_question and current_options:
        questions.append(
            {
                "question": current_question,
                "options": current_options,
                "answer": current_answer,
            }
        )

    return questions


def display_question(question_data, question_num, total_questions):
    """显示题目和选项"""
    print(f"\n{'=' * 60}")
    print(f"题目 {question_num}/{total_questions}")
    print(f"{'=' * 60}")
    print(f"\n{question_data['question']}\n")

    # 显示选项
    for i, option in enumerate(question_data["options"]):
        print(f"{i + 1}. {option}")

    print(f"\n{'-' * 60}")


def get_user_answer():
    """获取用户答案"""
    while True:
        try:
            choice = input("\n请输入你的答案 (1-4): ").strip()
            if choice in ["1", "2", "3", "4"]:
                return int(choice)
            else:
                print("请输入有效的数字 (1-4)")
        except ValueError:
            print("请输入有效的数字 (1-4)")


def check_answer(question_data, user_choice):
    """检查答案是否正确"""
    # 获取用户选择的选项字母
    user_answer = question_data["options"][user_choice - 1][0]  # A, B, C, or D
    correct_answer = question_data["answer"]

    is_correct = user_answer == correct_answer

    print(f"\n{'=' * 60}")
    if is_correct:
        print("✓ 回答正确！")
    else:
        print("✗ 回答错误！")
        print(
            f"正确答案是: {correct_answer}. {question_data['options'][ord(correct_answer) - ord('A')]}"
        )
    print(f"{'=' * 60}")

    return is_correct


def main():
    """主函数"""
    xml_file = r"D:\code\projects\Huawei\temp\word\document.xml"

    if not os.path.exists(xml_file):
        print(f"错误: 找不到文件 {xml_file}")
        return

    print("正在解析题目...")
    questions = parse_questions_from_xml(xml_file)

    if not questions:
        print("没有找到任何题目！")
        return

    print(f"成功解析 {len(questions)} 道题目！")

    # 随机打乱题目顺序
    random.shuffle(questions)

    score = 0
    total = len(questions)

    print("\n" + "=" * 60)
    print("欢迎使用华为知识测验程序！")
    print("类似驾考宝典，随机出题，测试你的知识掌握程度。")
    print("输入 1-4 选择答案，输入 'q' 退出程序。")
    print("=" * 60)

    for i, question in enumerate(questions, 1):
        display_question(question, i, total)

        user_choice = get_user_answer()
        if check_answer(question, user_choice):
            score += 1

        # 询问是否继续
        if i < total:
            continue_choice = input("\n按回车继续下一题，输入'q'退出: ").strip().lower()
            if continue_choice == "q":
                break

    # 显示最终成绩
    print(f"\n{'=' * 60}")
    print(f"测验结束！")
    print(f"你的得分: {score}/{i} ({score / i * 100:.1f}%)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
