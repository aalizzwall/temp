#!/usr/bin/env python3
"""
測試 PDF 答案解析 - 簡單版
"""

import fitz
import re

pdf_path = '/home/pascal/hermes-workspace/temp/exams/110_110_01_80_ANS.pdf'
doc = fitz.open(pdf_path)

answers = {}
q_num = None  # 當前題號
page_num = 0

for page in doc:
    page_num += 1
    text = page.get_text()
    
    # 清理特殊字符
    for ch in ['€', '₱', '£', '₽', '₿', '¥', '₦', '₨', '®', '™', '©', '\u3000']:
        text = text.replace(ch, '')
    
    # 按行分割
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        # 檢查是否為題號行（第 N 題）
        q_match = re.match(r'^第 (\d+) 題$', line)
        if q_match:
            # 如果之前有題號，記錄它的答案
            if q_num is not None and i > 0:
                prev_line = lines[i - 1]
                ans_match = re.match(r'^([ABCDF])$', prev_line)
                if ans_match:
                    answers[q_num] = ans_match.group(1)
                    print(f"第{q_num}題答案：{ans_match.group(1)}")
                else:
                    # 前一行不是答案，可能是題目內容
                    answers[q_num] = 'none'
                    
            # 設置新題號
            q_num = int(q_match.group(1))
            if q_num <= 80:
                print(f"  -> 新題號：第{q_num}題")
        else:
            # 不是題號行，檢查是否為答案
            ans_match = re.match(r'^([ABCDF])$', line)
            if ans_match and q_num is not None:
                if q_num not in answers:
                    print(f"第{q_num}題答案：{ans_match.group(1)}")
                answers[q_num] = ans_match.group(1)
                q_num = None  # 答案處理完，重置

doc.close()

print(f"\n總共解析了 {len(answers)} 個答案")
print("\n前 50 題答案樣本：")
for i in range(1, 51):
    print(f"第{i}題：{answers.get(i)}")
