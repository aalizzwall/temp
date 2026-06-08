#!/usr/bin/env python3
"""
護理師考題 JSONL 生成器 v7 - 使用一次讀取所有 PDF 內容
"""

import os
import re
import json
from pathlib import Path


def parse_txt_questions(txt_path):
    """讀取 txt 題目檔，返回題目列表"""
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    questions = []
    
    lines = content.split('\n')
    current_q_num = None
    current_q_text_parts = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        match = re.match(r'^(\d+)\s+', line)
        if match:
            if current_q_num is not None:
                questions.append({
                    'q_num': current_q_num,
                    'content': ' '.join(current_q_text_parts).strip()
                })
            current_q_num = int(match.group(1))
            current_q_text_parts = []
        else:
            current_q_text_parts.append(line)
    
    if current_q_num is not None:
        questions.append({
            'q_num': current_q_num,
            'content': ' '.join(current_q_text_parts).strip()
        })
    
    return questions


def parse_pdf_answers(pdf_path):
    """
    從 PDF 答案檔中提取所有答案（一次讀取所有頁面內容）。
    
    PDF 內容結構：
    題號
    答案
    第 1 題
    C
    第 2 題
    (無)
    第 3 題
    (無)
    ...
    第 80 題
    B
    第 81 題
    B
    ...
    
    解析策略：
    1. 提取所有「第 N 題」的位置
    2. 匹配對應的答案
    """
    import fitz
    
    doc = fitz.open(pdf_path)
    answers = {}  # key: q_num (int), value: answer (str or None)
    
    # 提取所有頁面的內容
    all_text = []
    for page in doc:
        all_text.append(page.get_text())
    
    full_text = '\n'.join(all_text)
    
    # 清理特殊字符
    for ch in ['€', '₱', '£', '₽', '₿', '¥', '₦', '₨', '®', '™', '©', '\u3000']:
        full_text = full_text.replace(ch, '')
    
    # 用正則提取所有「第 N 題」和它後面的答案
    # 模式：第 (\d+) 題 隨之而來的是答案 (A|B|C|D|E|F) 或 無 (下一個題號)
    pattern = re.compile(r'\b第 (\d+) 題\b', re.MULTILINE)
    
    matches = list(pattern.finditer(full_text))
    answers = {}
    
    for i, match in enumerate(matches):
        q_num = int(match.group(1))
        
        # 找到這個匹配的位置
        pos = match.end()
        
        # 往後找答案（最多 20 個字符）
        found_answer = None
        found_pos = None
        
        end_pos = pos + 20  # 限制搜索範圍
        
        while pos < end_pos:
            char = full_text[pos]
            if char in 'ABCDEF':
                found_answer = char
                found_pos = pos
                break
            elif char in '()\n ':
                pos += 1  # 跳過
            else:
                # 遇到其他字符，表示答案結束
                break
        
        if found_answer:
            answers[q_num] = found_answer
        else:
            answers[q_num] = None
    
    doc.close()
    return answers


def main():
    exam_dir = Path('/home/pascal/hermes-workspace/temp/exams')
    
    txt_files = sorted(exam_dir.glob('*.txt'))
    pdf_files = sorted(exam_dir.glob('*.pdf'))
    
    print(f"找到 {len(txt_files)} 個 txt 題目檔")
    print(f"找到 {len(pdf_files)} 個 PDF 答案檔")
    
    all_records = []
    
    for txt_file in txt_files:
        questions = parse_txt_questions(txt_file)
        
        txt_stem = txt_file.stem
        parts = txt_stem.split('_')
        batch = parts[0] if len(parts) >= 4 else txt_stem
        code = parts[2] if len(parts) >= 3 else "01"
        
        print(f"處理 {txt_file.name}: batch={batch}, code={code}, {len(questions)} 題")
        
        # 尋找對應的 PDF 檔案
        found_pdf = None
        for pdf_file in pdf_files:
            pdf_stem = pdf_file.stem
            if pdf_stem.endswith('_ANS'):
                pdf_parts = pdf_stem[:-4].split('_')
                pdf_batch = pdf_parts[0] if len(pdf_parts) > 0 else ""
                pdf_code = pdf_parts[2] if len(pdf_parts) > 2 else ""
                
                if pdf_batch == batch and pdf_code == code:
                    found_pdf = pdf_file
                    break
        
        if found_pdf:
            pdf_answers = parse_pdf_answers(found_pdf)
            
            for q in questions:
                record = {
                    'batch': batch,
                    'code': code,
                    'q_num': q['q_num'],
                    'question': q['content'],
                    'answer': pdf_answers.get(q['q_num']),
                    'pdf_source': str(found_pdf)
                }
                all_records.append(record)
        else:
            print(f"  警告：找不到對應的 PDF 檔案")
    
    # 去重並排序
    seen = set()
    unique_records = []
    for record in all_records:
        key = (record['batch'], record['code'], record['q_num'])
        if key not in seen:
            seen.add(key)
            unique_records.append(record)
    
    unique_records.sort(key=lambda x: (x['batch'], x['code'], x['q_num']))
    
    print(f"\n總共 {len(unique_records)} 道題目")
    
    total = len(unique_records)
    with_answer = sum(1 for r in unique_records if r['answer'] is not None)
    print(f"有答案的題目：{with_answer}/{total} = {with_answer/total*100:.1f}%")
    
    # 顯示前 50 筆樣本
    print("\n前 50 筆樣本：")
    for i, rec in enumerate(unique_records[:50]):
        print(json.dumps(rec, ensure_ascii=False))
        if i < 49:
            print("---")
    
    output_file = Path('/home/pascal/hermes-workspace/temp/exams/護理師考題.jsonl')
    with open(output_file, 'w', encoding='utf-8') as f:
        for rec in unique_records:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    
    print(f"\n已寫入 {output_file}")


if __name__ == '__main__':
    main()
