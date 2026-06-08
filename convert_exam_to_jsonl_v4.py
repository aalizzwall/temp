#!/usr/bin/env python3
"""
護理師考題 JSONL 生成器 v4
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
    """從 PDF 答案檔中提取答案（格式：題號\n答案 交替出現）"""
    import fitz  # PyMuPDF
    doc = fitz.open(pdf_path)
    answers = {}  # key: q_num (int), value: answer (str or None)
    
    for page in doc:
        # 提取文字
        text = page.get_text()
        
        # 清理特殊字符（單個字符替換）
        chars_to_remove = [
            '€', '₱', '£', '₽', '₿', '¥', '₦', '₨', 
            '®', '™', '©', '\u3000'
        ]
        for ch in chars_to_remove:
            text = text.replace(ch, '')
        
        # 分組處理：找出所有「第 N 題」對應的答案
        # 格式是：第 1 題\nC\n第 2 題\n（無答案）\n第 3 題\nD\n...
        lines = text.split('\n')
        
        # 找出所有題號
        q_num_pattern = re.compile(r'^(第\d+題|[0-9]+)[題道]$')
        answer_pattern = re.compile(r'^([ABCE]|[DF])$')
        
        current_q_num = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 檢查是否是題號行
            q_match = q_num_pattern.match(line)
            if q_match:
                # 如果之前有題號，保存它的答案
                if current_q_num is not None:
                    answers[current_q_num] = current_answer
                current_q_num = int(q_match.group(1))
                current_answer = None
            # 檢查是否是答案
            elif current_q_num is not None and answer_pattern.match(line):
                current_answer = line
            # 跳過其他行
            else:
                # 如果正在讀取答案，遇到非答案行則保存
                if current_q_num is not None and current_answer is not None:
                    answers[current_q_num] = current_answer
                current_q_num = None
                current_answer = None
    
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
    
    # 去重並排序（使用 (batch, code, q_num) 作為 key）
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
    
    # 統計各 batch 的題目覆蓋率
    print("\n題目覆蓋率統計（各 batch）:")
    batch_stats = {}
    for rec in unique_records:
        batch = rec['batch']
        key = (rec['batch'], rec['code'], rec['q_num'])
        has_answer = rec['answer'] is not None
        if batch not in batch_stats:
            batch_stats[batch] = {'total': 0, 'with_answer': 0}
        batch_stats[batch]['total'] += 1
        if has_answer:
            batch_stats[batch]['with_answer'] += 1
    
    for batch in sorted(batch_stats.keys()):
        stats = batch_stats[batch]
        coverage = stats['with_answer'] / stats['total'] * 100
        print(f"  Batch {batch}: {stats['total']} 題，{stats['with_answer']} 題有答案，覆蓋率 {coverage:.1f}%")
    
    # 統計各 code 的題目覆蓋率
    print("\n題目覆蓋率統計（各 code）:")
    code_stats = {}
    for rec in unique_records:
        code = rec['code']
        key = (rec['batch'], rec['code'], rec['q_num'])
        has_answer = rec['answer'] is not None
        if code not in code_stats:
            code_stats[code] = {'total': 0, 'with_answer': 0}
        code_stats[code]['total'] += 1
        if has_answer:
            code_stats[code]['with_answer'] += 1
    
    for code in sorted(code_stats.keys()):
        stats = code_stats[code]
        coverage = stats['with_answer'] / stats['total'] * 100
        print(f"  Code {code}: {stats['total']} 題，{stats['with_answer']} 題有答案，覆蓋率 {coverage:.1f}%")
    
    # 寫入完整的 JSONL
    output_file = Path('/home/pascal/hermes-workspace/temp/exams/護理師考題.jsonl')
    with open(output_file, 'w', encoding='utf-8') as f:
        for rec in unique_records:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    
    print(f"\n已寫入 {output_file}")
    print(f"總共 {len(unique_records)} 道題目")


if __name__ == '__main__':
    main()
