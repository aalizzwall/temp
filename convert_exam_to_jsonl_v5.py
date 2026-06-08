#!/usr/bin/env python3
"""
護理師考題 JSONL 生成器 v5 - 正確版
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
    """從 PDF 答案檔中提取答案（根據題號配對）"""
    import fitz
    doc = fitz.open(pdf_path)
    answers = {}  # key: q_num (int), value: answer (str or None)
    
    for page in doc:
        # 提取文字（lines 模式）
        text = page.get_text()
        
        # 清理特殊字符
        for ch in ['€', '₱', '£', '₽', '₿', '¥', '₦', '₨', '®', '™', '©', '\u3000']:
            text = text.replace(ch, '')
        
        lines = text.split('\n')
        
        # 使用 2x 滑動視窗來匹配題號和答案
        in_answer_block = False
        answer_value = None
        prev_q_num = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 檢查是否是「第 N 題」格式
            q_match = re.match(r'^第 (\d+) 題$', line)
            if q_match:
                q_num = int(q_match.group(1))
                # 保存上一題的答案
                if prev_q_num is not None:
                    answers[prev_q_num] = answer_value
                answer_value = None
                prev_q_num = q_num
                in_answer_block = True
                continue
            
            # 檢查是否是答案（A, B, C, D, E, F）
            ans_match = re.match(r'^([ABCE]|DF)$', line)
            if ans_match:
                if in_answer_block:
                    answer_value = ans_match.group(1)
                    in_answer_block = False
                else:
                    # 答案行不在題號行之後，忽略
                    pass
            else:
                # 如果是非題號、非答案的行，重置
                in_answer_block = False
    
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
                
                if pdf_batch == batch and pdf_subj == subj_batch and pdf_code == code:
                    found_pdf = pdf_file
                    break
        
        if found_pdf:
            # 讀取 PDF 答案
            pdf_answers = parse_pdf_answers(found_pdf)
            
            # 創建題目記錄
            for q in questions:
                q_num = q['q_num']
                record = {
                    'batch': batch,
                    'code': code,
                    'q_num': q_num,
                    'question': q['content'],
                    'answer': pdf_answers.get(q_num),
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
    
    # 統計答案覆蓋率
    total = len(unique_records)
    with_answer = sum(1 for r in unique_records if r['answer'] is not None)
    print(f"有答案的題目：{with_answer}/{total} = {with_answer/total*100:.1f}%")
    
    # 顯示前 50 筆樣本
    print("\n前 50 筆樣本：")
    for i, rec in enumerate(unique_records[:50]):
        print(json.dumps(rec, ensure_ascii=False))
        if i < 49:
            print("---")
    
    # 寫入 JSONL
    output_file = Path('/home/pascal/hermes-workspace/temp/exams/護理師考題.jsonl')
    with open(output_file, 'w', encoding='utf-8') as f:
        for rec in unique_records:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    
    print(f"\n已寫入 {output_file}")


if __name__ == '__main__':
    main()
