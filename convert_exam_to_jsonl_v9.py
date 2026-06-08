#!/usr/bin/env python3
"""
護理師考題 JSONL 生成器 v9 - 完整版
將 txt 題目和 PDF 答案配對，生成按考科分類的 JSONL
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
        
        # 檢查是否是新題目（開頭是數字 + 空格）
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
    從 PDF 答案檔中提取所有答案。
    
    PDF 格式：
    題目代號\n考試名稱\n科目名稱\n單選題數\n單選每題配分\n題號\n答案\n題號\n答案\n...\n複選題數\n複選每題配分\n標準答案\n備註
    
    解析策略：
    1. 找到「題號」行，然後交替尋找答案
    2. 格式：題號\n答案\n題號\n答案\n...\n
    3. 每個「題號」格式為「第 N 題」
    """
    import fitz
    
    doc = fitz.open(pdf_path)
    answers = {}  # key: q_num (int), value: answer (str or None)
    q_num = None  # 當前處理的題號
    
    for page in doc:
        # 使用 lines 模式提取文字
        text = page.get_text()
        
        # 清理特殊字符
        for ch in ['€', '₱', '£', '₽', '₿', '¥', '₦', '₨', '®', '™', '©', '\u3000']:
            text = text.replace(ch, '')
        
        lines = text.split('\n')
        
        # 找到所有「第 N 題」的行，以及它們的答案
        for i, line in enumerate(lines):
            # 檢查是否是題號行（第 N 題格式）
            q_num_match = re.match(r'^第 (\d+) 題$', line)
            if q_num_match:
                q_num = int(q_num_match.group(1))
                
                # 取下一行作為答案
                if i + 1 < len(lines):
                    ans_line = lines[i + 1].strip()
                    # 如果是單選答案 (A,B,C,D,E,F)，則保留
                    if ans_line and re.match(r'^([ABCDF])$', ans_line):
                        answers[q_num] = ans_line
                    else:
                        answers[q_num] = None
            # 如果是複選題（DF），直接記錄，不作為答案
            else:
                ans_match = re.match(r'^(DF)$', line)
                if ans_match and q_num is not None:
                    answers[q_num] = ans_match.group(1)  # 複選答案
                    q_num = None  # 重置，繼續尋找下一題
    
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
            # 從 PDF 中解析答案
            pdf_answers = parse_pdf_answers(found_pdf)
            
            # 為每個題目添加答案
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
