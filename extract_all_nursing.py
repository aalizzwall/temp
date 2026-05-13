import fitz
import os
import json
import re

exam_dir = '/home/pi/.hermes/temp/exams/'
files = ['112180_2101.pdf', '113100_2102.pdf', '113180_2101.pdf', '112110_2102.pdf', '110030_2104.pdf', '112030_2102.pdf', '111030_2104.pdf', '114100_2102.pdf', '113030_2101.pdf', '114170_2101.pdf', '115030_2101.pdf', '114030_2101.pdf', '111110_2104.pdf', '110110_2104.pdf']

def get_final_ans(session, code):
    # MOD > ANS
    for suffix in [f'MOD{code}.pdf', f'ANS{code}.pdf']:
        path = os.path.join(exam_dir, f'{session}_{suffix}')
        if os.path.exists(path):
            try:
                doc = fitz.open(path)
                return ''.join([page.get_text() for page in doc])
            except: pass
    return ''

all_data = []
for f in files:
    session = f.split('_')[0]
    code = f.split('_')[1].replace('.pdf', '')
    path = os.path.join(exam_dir, f)
    
    try:
        doc = fitz.open(path)
        text = ''.join([page.get_text() for page in doc])
        
        # 提取題目
        q_matches = re.findall(r'(\d+)\.(.*?)(?=\n\d+\.|$)', text, re.DOTALL)
        ans_text = get_final_ans(session, code)
        a_matches = re.findall(r'(\d+)\s*[\.（(]\s*([A-D])[\)）]?', ans_text)
        ans_map = {num: ans for num, ans in a_matches}
        
        for num, q_text in q_matches:
            all_data.append({
                'session': session,
                'num': num,
                'question': q_text.strip(),
                'answer': ans_map.get(num, '待確認'),
                'source_file': f
            })
    except Exception as e:
        print(f"Error processing {f}: {e}")

with open('/home/pi/.hermes/temp/all_nursing_questions.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"Successfully extracted {len(all_data)} questions to all_nursing_questions.json")
