#!/usr/bin/env python3
"""
簡化版 PDF 答案解析
"""

import re

pdf_path = '/home/pascal/hermes-workspace/temp/exams/110_110_01_80_ANS.pdf'

# 直接使用 pdfplumber（如果可用）或 fitz
try:
    from pdfplumber import pdf
    doc = pdf.open(pdf_path)
except:
    import fitz
    doc = fitz.open(pdf_path)

# 合併所有頁面的內容
if 'doc' not in dir() or 'pages' in dir():
    all_lines = []
    for page in doc:
        if hasattr(page, 'pages'):
            page = page.pages[0]
        text = page.read()[0].text  # pdfplumber 格式
        all_lines.extend(text.split('\n'))
else:
    page = doc[0]
    text = page.get_text()
    all_lines = text.split('\n')

# 清理特殊字符
for ch in ['€', '₱', '£', '₽', '₿', '¥', '₦', '₨', '®', '™', '©', '\u3000']:
    all_lines = [l for l in all_lines if ch not in l]

# 找到所有題號行
q_num_rows = []
for i, line in enumerate(all_lines):
    if re.match(r'第\s*(\d+)\s*題', line):
        q_num_rows.append((i, int(re.match(r'第\s*(\d+)\s*題', line).group(1))))

print(f"找到 {len(q_num_rows)} 個題號")
print("\n前 20 個題號行位置：")
for item in q_num_rows[:20]:
    print(f"  Line {item[0]}: 第{item[1]}題")

answers = {}
for idx, (pos, q_num) in enumerate(q_num_rows[:20]):
    # 題號行的下一行應該是答案（如果有的話）
    if pos + 1 < len(all_lines):
        next_line = all_lines[pos + 1].strip()
        ans_match = re.match(r'^([ABCDF])$', next_line)
        if ans_match:
            answers[q_num] = ans_match.group(1)
            print(f"  第{q_num}題答案：{ans_match.group(1)}")
        else:
            answers[q_num] = None
            print(f"  第{q_num}題答案：None")
    else:
        answers[q_num] = None

print("\n總共解析了", len(answers), "個答案")
