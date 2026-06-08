#!/usr/bin/env python3
"""
護理師考題 JSONL 生成器
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
            # 保存上一題
            if current_q_num is not None:
                questions.append({
                    'q_num': current_q_num,
                    'content': ' '.join(current_q_text_parts).strip()
                })
            current_q_num = int(match.group(1))
            current_q_text_parts = []
        else:
            current_q_text_parts.append(line)
    
    # 保存最後一題
    if current_q_num is not None:
        questions.append({
            'q_num': current_q_num,
            'content': ' '.join(current_q_text_parts).strip()
        })
    
    return questions


def parse_pdf_answers(pdf_path):
    """從 PDF 答案檔中提取答案"""
    import fitz  # PyMuPDF
    doc = fitz.open(pdf_path)
    answers = {}  # key: (q_num, subcode), value: answer
    
    for page in doc:
        # 提取文字
        text = page.get_text()
        
        # 清理 garbled 字元
        text = re.sub(r'[ÀÁÂÃÄÅĀàâäăąåēèēěēęĕēėîïīíìîłłöòóõôûüüÿŷſśßčćđđłńňñņŕŕřśşšżž]', '', text)
        text = re.sub(r'[āáǎàâäĀÀĒēĔĕĖêÉĚèĔĒēĘēĔĔīíìîÎîİïŒſĿſœšŠſ]', '', text)
        
        # 匹配答案行：題號 + 選項 + 答案
        lines = text.split('\n')
        current_q_num = None
        current_q_answers = []  # (q_num, code) -> ans
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 檢查是否是新題目（開頭是數字 + 空格 + 選項）
            match = re.match(r'^(\d+)\s+\((?:AB|A B|C|D|E|F)\)', line)
            if match:
                # 保存上一題的答案
                if current_q_num is not None:
                    for q_num, code, ans in current_q_answers:
                        key = (q_num, code)
                        if key not in answers:
                            answers[key] = ans
                current_q_num = int(match.group(1))
                current_q_answers = []
            elif current_q_num is not None:
                # 這是該題的答案行
                ans_match = re.search(r'\((?:AB|A B|C|D|E|F)\)([ABCDEF])', line)
                if ans_match:
                    current_q_answers.append((current_q_num, ans_match.group(1)))
        
        # 保存最後一題
        if current_q_num is not None:
            for q_num, code, ans in current_q_answers:
                key = (q_num, code)
                if key not in answers:
                    answers[key] = ans
    
    doc.close()
    return answers


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
        
        # 從檔名提取資訊
        txt_stem = txt_file.stem
        parts = txt_stem.split('_')
        batch = parts[0] if len(parts) >= 4 else txt_stem
        subj_batch = parts[1] if len(parts) >= 2 else "01"
        code = parts[2] if len(parts) >= 3 else "01"
        qnum = parts[3] if len(parts) >= 4 else txt_stem
        
        print(f"處理 {txt_file.name}: batch={batch}, code={code}, {len(questions)} 題")
        
        # 尋找對應的 PDF 檔案
        found_pdf = None
        for pdf_file in pdf_files:
            pdf_stem = pdf_file.stem
            if pdf_stem.endswith('_ANS'):
                pdf_parts = pdf_stem[:-4].split('_')
                pdf_batch = pdf_parts[0] if len(pdf_parts) > 0 else ""
                pdf_subj = pdf_parts[1] if len(pdf_parts) > 1 else ""
                pdf_code = pdf_parts[2] if len(pdf_parts) > 2 else ""
                pdf_qnum = pdf_parts[3] if len(pdf_parts) > 3 else ""
                
                if pdf_batch == batch and pdf_subj == subj_batch and pdf_code == code:
                    found_pdf = pdf_file
                    break
        
        if found_pdf:
            # 讀取 PDF 答案
            pdf_answers = parse_pdf_answers(found_pdf)
            
            # 創建題目記錄
            for q in questions:
                key = (q['q_num'], code)
                record = {
                    'batch': batch,
                    'code': code,
                    'q_num': q['q_num'],
                    'question': q['content'],
                    'answer': pdf_answers.get(key),
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
    
    # 顯示前 50 筆樣本
    print("\n前 50 筆樣本：")
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
