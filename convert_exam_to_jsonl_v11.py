#!/usr/bin/env python3
"""
護理師考題 JSONL 生成器 v11 - 正確解析 PDF 答案
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
    從 PDF 答案檔中提取答案。
    
    PDF 內容結構分析：
    - Line 11: '題號'
    - Line 12: '答案'
    - Line 13: '題號'
    - Line 14: '答案'
    - ...
    - Line 31: '第 1 題'
    - Line 32: 'C' -> 第 1 題答案
    - Line 33: '第 2 題'
    - Line 34: '第 3 題' -> 第 2 題答案為 None
    - Line 35: '第 4 題'
    - Line 36: '第 5 題' -> 第 3 題答案為 None
    
    關鍵發現：PDF 中的題號行（第 N 題）是連續的，每兩個題號行之間夾雜答案。
    
    解析策略：
    1. 先記錄所有「第 N 題」的位置
    2. 對於每個題號，看它後面一行的內容：如果是字母（A,B,C,D,E,F）則為答案，否則為 None
    """
    import fitz
    
    doc = fitz.open(pdf_path)
    answers = {}  # key: q_num (int), value: answer (str or None)
    q_num = None
    
    for page in doc:
        text = page.get_text()
        
        # 清理特殊字符
        for ch in ['€', '₱', '£', '₽', '₿', '¥', '₦', '₨', '®', '™', '©', '\u3000']:
            text = text.replace(ch, '')
        
        lines = text.split('\n')
        
        # 跳過前幾行的題頭（找到「第 1 題」開始）
        start_line = None
        for i, line in enumerate(lines):
            if re.match(r'第 \d+ 題$', line) or re.match(r'^第 (\d+) 題$', line):
                start_line = i
                break
        
        if start_line is None:
            # 嘗試找「第 1 題」
            for i, line in enumerate(lines):
                m = re.match(r'第 1 題', line)
                if m:
                    start_line = i
                    break
        
        if start_line is not None and start_line < len(lines):
            q_num = 1
            
            for i in range(start_line + 1, len(lines)):
                line = lines[i]
                
                # 檢查是否為題號行（第 N 題）
                if re.match(r'^第 (\d+) 題$', line):
                    # 前一行的答案（如果存在且是有效答案）
                    prev_line = lines[i - 1]
                    ans_match = re.match(r'^([ABCDF])$', prev_line)
                    if ans_match:
                        answers[1] = ans_match.group(1)
                    
                    new_q_num = int(re.match(r'^第 (\d+) 題$', line).group(1))
                    # 更新當前題號
                    q_num = new_q_num
                    if new_q_num <= 80:  # 只記錄單選題（1-80）
                        print(f"找到題號 {new_q_num}")
                
                # 當前題號的下一行如果為答案
                if q_num is not None and q_num <= 80:
                    current_line = lines[i]
                    ans_match = re.match(r'^([ABCDF])$', current_line)
                    if ans_match:
                        answers[q_num] = ans_match.group(1)
                        q_num = None  # 答案處理完，重置
                        # 找到答案了，記錄並跳過
                    else:
                        # 這一行不是答案，可能是下一題的題號
                        continue
        
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
