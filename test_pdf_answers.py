#!/usr/bin/env python3
"""
測試 PDF 答案解析
"""

import fitz
import re

pdf_path = '/home/pascal/hermes-workspace/temp/exams/110_110_01_80_ANS.pdf'
doc = fitz.open(pdf_path)

answers = {}

for page in doc:
    # 提取文字
    text = page.get_text()
    
    print("=" * 80)
    for i, line in enumerate(text.split('\n')):
        line = line.strip()
        if not line:
            continue
        
        # 檢查是否是題號行（「第 N 題」格式）
        q_match = re.match(r'^第 (\d+) 題$', line)
        if q_match:
            print(f"題號行：Q{q_match.group(1)}")
        # 檢查是否是答案
        else:
            ans_match = re.match(r'^([ABCE]|DF)$', line)
            if ans_match:
                print(f"答案行：{ans_match.group(1)}")

doc.close()
