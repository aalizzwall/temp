import fitz
import os
import json
import re

exam_dir = '/home/pi/.hermes/temp/exams/'
# 基礎醫學相關的 PDF 列表 (從之前的掃描得知)
files = ['115030_1101.pdf', '114100_1102.pdf', '114170_1101.pdf', '114030_1101.pdf']

# 藥理學強特徵關鍵字
pharm_keywords = [
    '藥物', '劑量', '受體', '拮抗', '激發', '副作用', '毒性', '半衰期', '代謝', '排出',
    'ACEI', 'ARB', 'Beta', 'Alpha', 'Digoxin', 'Insulin', 'Warfarin', 'Diuretic',
    '抗生素', '抗感染', '利尿劑', '心血管', '內分泌', '自律神經', '藥理'
]

def get_final_ans(session, code):
    for suffix in [f'MOD{code}.pdf', f'ANS{code}.pdf']:
        path = os.path.join(exam_dir, f'{session}_{suffix}')
        if os.path.exists(path):
            try:
                doc = fitz.open(path)
                return ''.join([page.get_text() for page in doc])
            except: pass
    return ''

all_pharm_data = []
for f in files:
    session = f.split('_')[0]
    code = f.split('_')[1].replace('.pdf', '')
    path = os.path.join(exam_dir, f)
    
    try:
        doc = fitz.open(path)
        text = ''.join([page.get_text() for page in doc])
        
        q_matches = re.findall(r'(\d+)\.(.*?)(?=\n\d+\.|$)', text, re.DOTALL)
        ans_text = get_final_ans(session, code)
        a_matches = re.findall(r'(\d+)\s*[\.（(]\s*([A-D])[\)）]?', ans_text)
        ans_map = {num: ans for num, ans in a_matches}
        
        for num, q_text in q_matches:
            # 智能判定是否為藥理學題目
            if any(kw in q_text for kw in pharm_keywords):
                all_pharm_data.append({
                    'session': session,
                    'num': num,
                    'question': q_text.strip(),
                    'answer': ans_map.get(num, '待確認'),
                    'source_file': f
                })
    except Exception as e:
        print(f"Error processing {f}: {e}")

with open('/home/pi/.hermes/temp/pharm_mapped.json', 'w', encoding='utf-8') as f:
    json.dump(all_pharm_data, f, ensure_ascii=False, indent=2)

print(f"Successfully extracted {len(all_pharm_data)} pharmacology questions.")
