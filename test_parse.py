#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试解析题目
"""

import xml.etree.ElementTree as ET
import re
import os


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


def main():
    xml_file = r"D:\code\projects\Huawei\temp\word\document.xml"

    if not os.path.exists(xml_file):
        print(f"错误: 找不到文件 {xml_file}")
        return

    print("正在解析题目...")
    questions = parse_questions_from_xml(xml_file)

    print(f"成功解析 {len(questions)} 道题目！")

    # 显示前5道题
    print("\n前5道题目示例:")
    for i, q in enumerate(questions[:5], 1):
        print(f"\n题目 {i}: {q['question']}")
        for opt in q["options"]:
            print(f"  {opt}")
        print(f"正确答案: {q['answer']}")


if __name__ == "__main__":
    main()
