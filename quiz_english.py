#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Huawei Knowledge Quiz Program - Similar to Driving Test App
Extracts questions from docx XML, random quiz, supports 1234 answer selection
"""

import xml.etree.ElementTree as ET
import random
import re
import os


def parse_questions_from_xml(xml_file):
    """Parse XML file to extract questions, options and answers"""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Namespace
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

    questions = []
    current_question = None
    current_options = []
    current_answer = None

    # Iterate through all paragraphs
    for para in root.findall(".//w:p", ns):
        # Get paragraph text
        text = ""
        for run in para.findall(".//w:r", ns):
            for t in run.findall(".//w:t", ns):
                if t.text:
                    text += t.text

        text = text.strip()
        if not text:
            continue

        # Check if it's a question (starts with number followed by "、" or ".")
        if re.match(r"^\d+[、.]", text):
            # Save previous question
            if current_question and current_options:
                questions.append(
                    {
                        "question": current_question,
                        "options": current_options,
                        "answer": current_answer,
                    }
                )

            # Start new question
            current_question = text
            current_options = []
            current_answer = None

        # Check if it's an option (A. B. C. D.)
        elif re.match(r"^[A-D][.]", text):
            # Check for yellow highlight
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
                # Extract option letter
                current_answer = text[0]  # A, B, C, or D

    # Save last question
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
    """Display question and options"""
    print(f"\n{'=' * 60}")
    print(f"Question {question_num}/{total_questions}")
    print(f"{'=' * 60}")
    print(f"\n{question_data['question']}\n")

    # Display options
    for i, option in enumerate(question_data["options"]):
        print(f"{i + 1}. {option}")

    print(f"\n{'-' * 60}")


def get_user_answer():
    """Get user answer"""
    while True:
        try:
            choice = input("\nEnter your answer (1-4): ").strip()
            if choice in ["1", "2", "3", "4"]:
                return int(choice)
            else:
                print("Please enter a valid number (1-4)")
        except ValueError:
            print("Please enter a valid number (1-4)")


def check_answer(question_data, user_choice):
    """Check if answer is correct"""
    # Get user's selected option letter
    user_answer = question_data["options"][user_choice - 1][0]  # A, B, C, or D
    correct_answer = question_data["answer"]

    is_correct = user_answer == correct_answer

    print(f"\n{'=' * 60}")
    if is_correct:
        print("✓ Correct!")
    else:
        print("✗ Wrong!")
        print(
            f"Correct answer: {correct_answer}. {question_data['options'][ord(correct_answer) - ord('A')]}"
        )
    print(f"{'=' * 60}")

    return is_correct


def main():
    """Main function"""
    xml_file = r"D:\code\projects\Huawei\temp\word\document.xml"

    if not os.path.exists(xml_file):
        print(f"Error: File not found {xml_file}")
        return

    print("Parsing questions...")
    questions = parse_questions_from_xml(xml_file)

    if not questions:
        print("No questions found!")
        return

    print(f"Successfully parsed {len(questions)} questions!")

    # Randomize question order
    random.shuffle(questions)

    score = 0
    total = len(questions)

    print("\n" + "=" * 60)
    print("Welcome to Huawei Knowledge Quiz!")
    print("Similar to driving test app, random questions, test your knowledge.")
    print("Enter 1-4 to select answer, enter 'q' to quit.")
    print("=" * 60)

    for i, question in enumerate(questions, 1):
        display_question(question, i, total)

        user_choice = get_user_answer()
        if check_answer(question, user_choice):
            score += 1

        # Ask to continue
        if i < total:
            continue_choice = (
                input("\nPress Enter for next question, enter 'q' to quit: ")
                .strip()
                .lower()
            )
            if continue_choice == "q":
                break

    # Show final score
    print(f"\n{'=' * 60}")
    print(f"Quiz completed!")
    print(f"Your score: {score}/{i} ({score / i * 100:.1f}%)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
