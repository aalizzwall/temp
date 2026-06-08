#!/usr/bin/env python3
"""
護理師考題 JSONL 生成器 v10 - 重新設計 PDF 解析
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
    
    PDF 內容結構：
    - 題頭（類科名稱、科目名稱、題號等）
    - 題號行 + 答案行交替：第 1 題\nC\n第 2 題\n...\n
    - 題號行（第 81-100 題，複選題）
    - 複選題答案：DF
    
    解析策略：
    1. 先解析單選題答案（第 1-80 題）
    2. 跳過中間的題號標題行
    3. 直接解析每個「第 N 題」行，取下一行作為答案
    """
    import fitz
    
    doc = fitz.open(pdf_path)
    answers = {}  # key: q_num (int), value: answer (str or None)
    q_num = None  # 當前處理的單選題題號
    
    for page in doc:
        text = page.get_text()
        
        # 清理特殊字符
        for ch in ['€', '₱', '£', '₽', '₿', '¥', '₦', '₨', '®', '™', '©', '\u3000']:
            text = text.replace(ch, '')
        
        lines = text.split('\n')
        
        # 找到「題號」行和「答案」行的位置
        # 單選題答案行會包含 A,B,C,D,E,F
        # 複選題答案行會是 DF
        
        for i, line in enumerate(lines):
            # 檢查是否是新題號行
            q_num_match = re.match(r'^第 (\d+) 題$', line)
            if q_num_match:
                # 如果之前有正在處理的題號，記錄它的答案
                if q_num is not None and i > 0:
                    prev_q_num = q_num
                    # 前一行的答案（如果是 A,B,C,D,E,F 其中之一）
                    prev_line = lines[i - 1]
                    prev_match = re.match(r'^([ABCDF])$', prev_line)
                    if prev_match:
                        answers[prev_q_num] = prev_match.group(1)
                    else:
                        # 前一行的內容，繼續尋找下一行是否有答案
                        pass
                    
                    q_num = int(q_num_match.group(1))
            
            # 檢查當前行是否為答案
            if q_num is not None:
                ans_match = re.match(r'^([ABCDF])$', line)
                if ans_match:
                    answers[q_num] = ans_match.group(1)
                    q_num = None  # 答案處理完畢，重置
                elif re.match(r'^DF$', line):
                    # 複選答案
                    answers[q_num] = 'DF'
                    q_num = None
    
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
