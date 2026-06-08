#!/usr/bin/env python3
import fitz
pdf_path = '/home/pascal/hermes-workspace/temp/exams/110_110_01_80_ANS.pdf'
doc = fitz.open(pdf_path)
page = doc[0]
words = page.get_text('words')
print("PDF 內容（words 模式）：")
for word in words[:100]:
    item_id, x0, y0, x1, y1 = word
    print(f"{item_id}: [{x0:5.1f},{y0:5.1f},{x1:5.1f},{y1:5.1f}] '{word[4]}'")
doc.close()
