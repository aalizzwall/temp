#!/usr/bin/env python3
"""
護理師考題整理腳本
將 txt 題目和 PDF 答案配對，生成 JSONL 格式
"""

import os
import re
import json
from pathlib import Path


def parse_txt_questions(txt_path):
    """讀取 txt 題目檔，返回題目列表"""
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正則表達式匹配題目（N 題目內容）
    pattern = re.compile(r'^(\d+)\s+([\s\S]*?)(?=^\d+\s|\Z)', re.MULTILINE)
    
    questions = []
    for match in pattern.finditer(content):
        q_num = int(match.group(1))
        q_text = match.group(2).strip()
        questions.append({
            'q_num': q_num,
            'content': q_text
        })
    
    return questions


def parse_pdf_answers(pdf_path):
    """讀取 PDF 答案檔（純文字格式），返回答案列表"""
    answers = {}
    
    with open(pdf_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配題號和答案的模式：第 N 題 [A/B/C/D]
    pattern = re.compile(r'^第 (\d+) 題 (\d)')
    
    for match in pattern.finditer(content):
        q_num = int(match.group(1))
        ans = match.group(2)
        answers[q_num] = ans
    
    return answers


def convert_to_pdf_text_answer(pdf_path):
    """將 PDF 答案轉換為文本格式"""
    with open(pdf_path, 'rb') as f:
        import fitz
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
    
    # 清理不必要的內容，只保留「第 N 題 X」格式的對
    lines = []
    for line in text.split('\n'):
        # 匹配「第 N 題」或「N 題」後的單獨字母
        match = re.match(r'^第\s+(\d+) 題\s+(?=[ABCDEF])', line.strip())
        if match:
            q_num = int(match.group(1))
            lines.append(f"{q_num} {match.group(2)}")
    
    return '\n'.join(lines)


def main():
    exam_dir = Path('/home/pascal/hermes-workspace/temp/exams')
    
    # 收集所有 txt 和 PDF
    txt_files = sorted(exam_dir.glob('*.txt'))
    pdf_files = sorted(exam_dir.glob('*.pdf'))
    
    print(f"找到 {len(txt_files)} 個 txt 題目檔")
    print(f"找到 {len(pdf_files)} 個 PDF 答案檔")
    
    all_questions = []
    all_answers = []
    
    # 解析所有題目
    for txt_file in txt_files:
        questions = parse_txt_questions(txt_file)
        all_questions.extend(questions)
    
    # 解析所有 PDF（轉換為文本）
    for pdf_file in pdf_files:
        # 先檢查是否有對應的 txt
        txt_name = pdf_file.stem.replace('_ANS', '')
        txt_path = exam_dir / f"{txt_name}.txt"
        
        if txt_path.exists():
            questions = parse_txt_questions(txt_path)
            
            # 獲取 PDF 答案
            pdf_text = convert_to_pdf_text_answer(pdf_file)
            answer_dict = {}
            for line in pdf_text.split('\n'):
                match = re.match(r'^(\d+)\s+([ABCDEF])', line.strip())
                if match:
                    q_num = int(match.group(1))
                    ans = match.group(2)
                    answer_dict[q_num] = ans
            
            # 配對題目和答案
            for q in questions:
                if q['q_num'] in answer_dict:
                    answer_line = {
                        'q_num': q['q_num'],
                        'answer': answer_dict[q['q_num']],
                        'pdf_source': str(pdf_file)
                    }
                else:
                    answer_line = {
                        'q_num': q['q_num'],
                        'answer': None,
                        'pdf_source': str(pdf_file)
                    }
                
                answer_line['question_text'] = q['content']
                all_answers.append(answer_line)
        else:
            # 沒有對應 txt 的 PDF，嘗試直接解析 PDF
            pdf_text = convert_to_pdf_text_answer(pdf_file)
            for match in re.finditer(r'^第 (\d+) 題 (\d)', pdf_text):
                q_num = int(match.group(1))
                ans = match.group(2)
                all_answers.append({
                    'q_num': q_num,
                    'answer': ans,
                    'pdf_source': str(pdf_file)
                })
    
    # 去重並排序
    seen = set()
    unique_answers = []
    for ans in all_answers:
        key = (ans['q_num'], ans.get('pdf_source'))
        if key not in seen:
            seen.add(key)
            unique_answers.append(ans)
    
    # 按題號排序
    unique_answers.sort(key=lambda x: x['q_num'])
    
    print(f"總共 {len(unique_answers)} 道題目")
    
    # 輸出前 50 筆
    for i, ans in enumerate(unique_answers[:50]):
        print(json.dumps(ans, ensure_ascii=False))
        if i < 49:
            print("---")
    
    # 寫入完整的 JSONL
    output_file = Path('/home/pascal/hermes-workspace/temp/exams/護理師考題.jsonl')
    with open(output_file, 'w', encoding='utf-8') as f:
        for ans in unique_answers:
            f.write(json.dumps(ans, ensure_ascii=False) + '\n')
    
    print(f"\n已寫入 {output_file}")
    print(f"總共 {len(unique_answers)} 道題目")


if __name__ == '__main__':
    main()
