#!/usr/bin/env python3
"""
調試 PDF 格式
"""

import fitz

pdf_path = '/home/pascal/hermes-workspace/temp/exams/110_110_01_80_ANS.pdf'
doc = fitz.open(pdf_path)

page = doc[0]
text = page.get_text()
lines = text.split('\n')

print(f"PDF 共有 {len(lines)} 行")
print("\n前 50 行：")
for i, line in enumerate(lines[:50]):
    print(f"{i:2d}: '{line}'")

doc.close()
