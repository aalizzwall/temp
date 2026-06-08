#!/usr/bin/env python3
"""
護理師考題整理腳本
將 txt 題目檔和對應的 PDF 答案檔配對，生成 JSONL 格式
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
    pattern = re.compile(r'^(\d+)\s+([\s\S]*?)(?=^\d+\s+|\Z)', re.MULTILINE)
    
    questions = []
    for match in pattern.finditer(content):
        q_num = int(match.group(1))
        q_text = match.group(2).strip()
        questions.append({
            'q_num': q_num,
            'content': q_text
        })
    
    return questions


def main():
    exam_dir = Path('/home/pascal/hermes-workspace/temp/exams')
    
    # 收集所有 txt 和 PDF
    txt_files = sorted(exam_dir.glob('*.txt'))
    pdf_files = sorted(exam_dir.glob('*.pdf'))
    
    print(f"找到 {len(txt_files)} 個 txt 題目檔")
    print(f"找到 {len(pdf_files)} 個 PDF 答案檔")
    
    all_records = []
    
    for txt_file in txt_files:
        questions = parse_txt_questions(txt_file)
        
        # 從檔名提取資訊：batch_subj_code_qnum
        # 例：110_110_01_80.txt -> batch=110, subj=110, code=01, qnum=80
        txt_stem = txt_file.stem
        parts = txt_stem.split('_')
        batch = parts[0] if len(parts) >= 4 else txt_stem
        subj_code = parts[1] if len(parts) >= 2 else "01"
        code = parts[2] if len(parts) >= 3 else "01"
        qnum = parts[3] if len(parts) >= 4 else txt_stem
        
        print(f"處理 {txt_file.name}: batch={batch}, code={code}, 共 {len(questions)} 題")
        
        # 尋找對應的 PDF 檔案
        # 格式：{batch}_{subj_code}_{code}_{qnum}_ANS.pdf
        # 需要遍歷所有 PDF 找到匹配檔名的
        found_pdf = None
        for pdf_file in pdf_files:
            pdf_stem = pdf_file.stem
            # 檢查 PDF 檔名格式
            if pdf_stem.endswith('_ANS'):
                pdf_parts = pdf_stem[:-4].split('_')  # 去掉 _ANS
                if len(pdf_parts) >= 3:
                    pdf_batch = pdf_parts[0] if len(pdf_parts) > 0 else ""
                    pdf_subj = pdf_parts[1] if len(pdf_parts) > 1 else ""
                    pdf_code = pdf_parts[2] if len(pdf_parts) > 2 else ""
                    pdf_qnum = pdf_parts[3] if len(pdf_parts) > 3 else ""
                    
                    if pdf_batch == batch and pdf_subj == subj_code and pdf_code == code:
                        found_pdf = pdf_file
                        break
        
        if found_pdf:
            # 讀取 PDF 答案（手動轉成文字）
            # 這裡我們假設已經有轉換好的答案文
            answer_file = Path('/home/pascal/hermes-workspace/temp/exams/answers.txt')
            
            # 讀取答案文字檔
            answers = {}
            if answer_file.exists():
                with open(answer_file, 'r', encoding='utf-8') as af:
                    for line in af:
                        match = re.match(r'^(\d+)\s+([ABCDEF])\s*(.*)', line.strip())
                        if match:
                            ans_qnum = int(match.group(1))
                            ans = match.group(2)
                            code = match.group(3).strip() if match.group(3) else "01"
                            answers[(ans_qnum, code)] = ans
            
            # 創建題目記錄
            for q in questions:
                key = (q['q_num'], code)
                record = {
                    'batch': batch,
                    'code': code,
                    'q_num': q['q_num'],
                    'question_text': q['content'],
                    'answer': answers.get(key),
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
    
    # 按 batch -> code -> q_num 排序
    unique_records.sort(key=lambda x: (x['batch'], x['code'], x['q_num']))
    
    print(f"\n總共 {len(unique_records)} 道題目")
    
    # 輸出前 50 筆
    for i, rec in enumerate(unique_records[:50]):
        print(json.dumps(rec, ensure_ascii=False))
        if i < 49:
            print("---")
    
    # 寫入完整的 JSONL
    output_file = Path('/home/pascal/hermes-workspace/temp/exams/護理師考題.jsonl')
    with open(output_file, 'w', encoding='utf-8') as f:
        for rec in unique_records:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    
    print(f"\n已寫入 {output_file}")
    print(f"總共 {len(unique_records)} 道題目")


if __name__ == '__main__':
    main()
