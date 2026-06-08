#!/usr/bin/env python3
import fitz

pdf_path = '/home/pascal/hermes-workspace/temp/exams/110_110_01_80_ANS.pdf'
doc = fitz.open(pdf_path)

# 使用 raw 模式
page = doc[0]
raw_text = page.get_text('raw')

print("Raw text 前 500 字元：")
print(raw_text[:500])

doc.close()
