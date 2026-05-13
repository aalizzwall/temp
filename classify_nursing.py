import json

with open('/home/pi/.hermes/temp/all_nursing_questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

admin_keywords = ['法律', '行政', '管理', '品質', 'JCI', '倫理', '知情', '同意', '監護', '權限', '職責', '責任', '糾紛', '法規']

results = {'BasicNursing': [], 'AdminNursing': [], 'Unclassified': []}

for item in data:
    q = item['question']
    if any(kw in q for kw in admin_keywords):
        results['AdminNursing'].append(item)
    else:
        results['BasicNursing'].append(item)

with open('/home/pi/.hermes/temp/classified_nursing.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Classification complete: Admin={len(results['AdminNursing'])}, Basic={len(results['BasicNursing'])}, Unclassified={len(results['Unclassified'])}")
