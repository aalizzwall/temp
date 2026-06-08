#!/usr/bin/env python3
import fitz
import re

pdf_path = '/home/pascal/hermes-workspace/temp/exams/110_110_01_80_ANS.pdf'
doc = fitz.open(pdf_path)

page = doc[0]
text = page.get_text()

# 清理特殊字符
for ch in ['€', '₱', '£', '₽', '₿', '¥', '₦', '₨', '®', '™', '©', '\u3000']:
    text = text.replace(ch, '')

lines = text.split('\n')

# 找出所有「第 N 題」的行（PDF 中格式為「第 N 題」，沒有空格）
q_num_rows = []
for i, line in enumerate(lines):
    match = re.match(r'^第 (\d+) 題$', line)
    if match:
        q_num_rows.append((i, int(match.group(1))))

print(f"找到 {len(q_num_rows)} 個題號行")
print("前 10 個題號行：", q_num_rows[:10])

# 為每個題號找出答案
answers = {}
for idx, (q_num, row_idx) in q_num_rows:
    next_idx = row_idx + 1
    
    if next_idx < len(lines):
        next_line = lines[next_idx].strip()
        
        # 如果是答案行（A, B, C, D, E, F）
        ans_match = re.match(r'^([ABCDEF])$', next_line)
        if ans_match:
            answers[q_num] = ans_match.group(1)
        else:
            answers[q_num] = None
    else:
        answers[q_num] = None

print(f"\n前 20 題答案：")
for i in range(1, 21):
    print(f"第{i}題：{answers.get(i)}")

doc.close()
