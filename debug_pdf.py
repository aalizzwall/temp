#!/usr/bin/env python3
import fitz
import re

pdf_path = '/home/pascal/hermes-workspace/temp/exams/110_110_01_80_ANS.pdf'
doc = fitz.open(pdf_path)

page = doc[0]
text = page.get_text()

# 不要清理特殊字符
lines = text.split('\n')

# 找出所有「第 N 題」的行
print("前 100 行：")
for i, line in enumerate(lines[:100]):
    print(f"Line {i}: '{line}'")
    if re.match(r'^第 \d+ 題$', line):
        print(f"  ^^^ 匹配！")
    
    match = re.match(r'^第 (\d+) 題$', line)
    if match:
        print(f"  ^^^ 正則匹配成功！q_num={match.group(1)}")

doc.close()
