#!/usr/bin/env python3
"""Generate HTML textbook for nursing exam subject 110 (基礎醫學)."""
import json
from collections import defaultdict

# Load data
index_file = "/home/pascal/hermes-workspace/nursing_output/indexes/nursing_index_110.jsonl"
entries = []
with open(index_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            entries.append(json.loads(line))

def get_year(fname):
    return fname.split('_')[0][:3]

def get_exam_label(fname):
    parts = fname.split('_')
    year = parts[0][:3]
    month = parts[1][:2]
    return f"國{year}年{month}月", year, month

# Group by topic
topic_groups = defaultdict(list)
for e in entries:
    topic_groups[e['topic_tag']].append(e)

# Major category mapping
major_categories = {
    '[解剖學': ('A', '解剖學'),
    '[生理學': ('B', '生理學'),
    '[病理學': ('C', '病理學'),
    '[藥理學': ('D', '藥理學'),
    '[微生物': ('E', '微生物學'),
    '[免疫': ('F', '免疫學'),
    '[生物': ('G', '生物化學與細胞生物學'),
    '[基礎': ('Z', '基礎醫學（一般）'),
}

def get_major(tag):
    for prefix, (order, name) in major_categories.items():
        if tag.startswith(prefix):
            return order, name
    return 'Z', '其他'

# Build category -> topics -> questions
cat_data = defaultdict(lambda: defaultdict(list))
for tag, qs in topic_groups.items():
    order, cat_name = get_major(tag)
    cat_data[(order, cat_name)][tag] = qs

# Sort categories
sorted_cats = sorted(cat_data.keys())

# Key points database (abbreviated - covers main topics)
key_points = {
    '[解剖學 骨骼系統]': '長骨結構含骨骺板（縱向生長）、骨外膜、骨內膜。椎骨特徵：頸椎有橫突孔、胸椎有肋凹、腰椎棘突呈板狀。薦椎由5個薦椎融合而成。',
    '[解剖學 器官與組織結構]': '四大組織：上皮、結締、肌肉、神經。上皮分被覆上皮、腺上皮。結締組織含血液、骨、軟骨、脂肪。',
    '[解剖學 消化系統]': '消化道：口腔→咽→食道→胃→小腸（十二指腸、空腸、迴腸）→大腸。消化腺：肝、胰、唾液腺。肝是最大的內分泌腺。',
    '[解剖學 生殖系統]': '男性：睪丸、附睪、輸精管、精囊、前列腺。女性：卵巢、輸卵管、子宮、陰道。',
    '[解剖學 心血管系統]': '心臟四腔：左右心房、左右心室。主要血管：主動脈、肺動脈、肺靜脈、腔靜脈。冠狀動脈供應心肌血液。',
    '[解剖學 泌尿系統]': '腎臟結構：腎髓質、腎皮質、腎盂。腎單位含腎絲球、近曲小管、亨利氏環、遠曲小管。',
    '[解剖學 神經系統]': '中樞神經：大腦、小腦、腦幹、脊髓。周邊神經：12對腦神經、31對脊神經。自主神經：交感、副交感。',
    '[解剖學 消化系統]': '消化道由口腔至肛門，附屬器官含肝、膽、胰。小腸是主要吸收部位。',
    '[解剖學 人體解剖]': '解剖學方位：頭側/尾側、腹側/背側、近端/遠端、內側/外側。身體腔：顱腔、胸腔、腹腔、骨盆腔。',
    '[解剖學 感覺器官]': '眼：角膜、虹膜、晶狀體、視網膜。耳：外耳、中耳（三聽小骨）、內耳（前庭、半規管、蝸牛）。',
    '[解剖學 細胞結構]': '細胞器：細胞核（DNA）、粒線體（ATP）、內質網、高基氏體、溶酶體、核糖體。細胞膜：磷脂雙層。',
    '[解剖學 肌肉系統]': '骨骼肌（隨意肌）、平滑肌（不隨意肌）、心肌。肌肉附著：原發點（origin）、止點（insertion）。',
    '[解剖學 呼吸系統]': '呼吸道：鼻→咽→喉→氣管→支氣管→細支氣管→肺泡。肺含兩葉（右三左二）。',
    '[解剖學 皮膚與附屬器]': '皮膚分表皮（角化層顆粒層棘細胞層基底層）、真皮、皮下組織。附屬器：毛髮、指甲、汗腺、皮脂腺。',
    '[解剖學 解剖結構]': '各種解剖結構的辨識與功能。',
    '[解剖學 生殖系統]': '男性生殖系統：睪丸、附睪、輸精管、精囊腺、前列腺、陰莖。女性：卵巢、輸卵管、子宮、陰道。',
    '[生理學 細胞生理]': '細胞膜運輸：被動運輸（擴散、滲透）、主動運輸（Na+/K+ pump）、胞吞/胞吐。細胞信號傳導：G蛋白偶聯受體、酪胺酸激酶受體。',
    '[生理學 神經生理]': '動作電位：去極化→反轉→再極化→超極化。突觸傳遞：神經傳導物質釋放→結合受體→後突觸電位。',
    '[生理學 內分泌生理]': '內分泌腺：腦下垂體、甲狀腺、副甲狀腺、腎上腺、胰臟、性腺。荷爾蒙作用機制：第二信使系統。',
    '[生理學 免疫學]': '先天免疫：物理屏障、吞噬細胞、NK細胞、補體系統。適應免疫：T細胞、B細胞、抗體。',
    '[生理學 消化生理]': '消化過程：機械性消化（咀嚼、蠕動）+ 化學性消化（酵素）。胃酸（HCl）、胃蛋白酶、膽汁、胰液。',
    '[生理學 呼吸生理]': '呼吸循環：通氣→氣體交換→氣體運輸。肺活量、功能殘氣量。血中O2和CO2運輸方式。',
    '[生理學 血液生理]': '血液組成：紅血球（攜氧）、白血球（免疫）、血小板（凝血）、血漿。血型和Rh因子。',
    '[生理學 循環生理]': '心輸出量 = 每搏輸出量 × 心跳速率。血壓 = 心輸出量 × 周邊阻力。自律調節機制。',
    '[生理學 代謝與能量]': '細胞呼吸：糖解作用→克雷氏迴路→電子傳遞鏈。ATP生成。有氧/無氧代謝。',
    '[生理學 腎臟生理]': '腎絲球過濾→近曲小管重吸收→亨利氏環→遠曲小管→集合管。尿液形成三步驟：過濾、重吸收、分泌。',
    '[生理學 生殖生理]': '男性：睪固酮、精子發生。女性：月經週期、排卵、雌二醇、黃體素。',
    '[生理學 血液與凝血]': '凝血瀑布：內源性/外源性途徑→共同途徑→纖維蛋白凝塊。紅血球生成素（EPO）。',
    '[生理學 免疫生理]': '抗原呈遞、T細胞活化、B細胞產生抗體、記憶細胞形成。細胞性免疫 vs 液體性免疫。',
    '[生理學 呼吸系統]': '呼吸調節：延髓呼吸中樞、腦橋。化學感受器：CO2、H+、O2。',
    '[生理學 營養與維生素]': '維生素分類：水溶性（B群、C）、脂溶性（A、D、E、K）。礦物質：鈣、鐵、鋅。',
    '[生理學 心血管生理]': '心電圖：P波、QRS波群、T波。心臟週期：收縮期、舒張期。自律性。',
    '[生理學 泌尿系統]': '腎臟功能：排泄代謝廢物、調節水分和電解質、維持酸鹼平衡、分泌荷爾蒙。',
    '[生理學 微生物學]': '微生物基本特性：細菌、病毒、真菌、寄生蟲的結構與生長。',
    '[生理學 藥理機制]': '藥物作用機制：受體結合、酵素抑制、離子通道調節。',
    '[生理學 酸鹼平衡]': '血液pH 7.35-7.45。緩衝系統：碳酸氫鹽、磷酸鹽、蛋白質。呼吸性和代謝性酸/鹼中毒。',
    '[生理學 循環系統]': '循環系統整體功能：體循環、肺循環。微循環與淋巴系統。',
    '[生理學 肌肉生理]': '肌肉收縮：肌絲滑動理論、興奮-收縮耦聯。肌動蛋白、肌球蛋白、鈣離子。',
    '[生理學 神經系統]': '中樞神經系統功能：大腦皮質分區、小腦平衡協調、腦幹生命徵象。',
    '[生理學 內分泌與荷爾蒙]': '內分泌系統總覽：下視丘-腦下垂體軸、甲狀腺、腎上腺、胰臟。',
    '[生理學 生殖系統]': '生殖系統生理：性腺功能、生殖荷爾蒙、生殖週期。',
    '[病理學 炎症反應]': '炎症五徵：紅、腫、熱、痛、功能喪失。急性炎症 vs 慢性炎症。炎症介質：組織胺、前列腺素、細胞激素。',
    '[病理學 腫瘤學]': '腫瘤特徵：不受控增生、侵襲、轉移。良性 vs 惡性。致癌因子：化學、物理、病毒。',
    '[病理學 循環系統病理]': '心血管疾病：動脈硬化、高血壓、冠心病、心肌梗塞、中風、心衰竭。',
    '[病理學 組織變化]': '細胞適應：肥大、增生、萎縮、化生。細胞死亡：壞死、凋亡。',
    '[病理學 中毒與環境]': '毒物代謝：肝臟解毒、腎臟排泄。環境毒素：重金屬、農藥、空氣污染。',
    '[病理學 發炎與免疫疾病]': '自體免疫疾病：類風濕性關節炎、紅斑性狼瘡、多發性硬化。過敏反應分類。',
    '[病理學 腫瘤與癌症]': '癌症分類：上皮來源（癌）、間葉來源（肉瘤）。TNM分期。癌症治療：手術、化學治療、放射治療、標靶治療。',
    '[病理學 遺傳疾病]': '遺傳模式：常染色體顯性/隱性、X染色體連鎖。染色體異常：唐氏症、透納症。',
    '[病理學 免疫疾病]': '免疫缺陷：原發性（SCID）、獲得性（AIDS）。免疫失調疾病。',
    '[病理學 神經系統疾病]': '中風、帕金森氏症、阿茲海默症、多發性硬化、癫痫。',
    '[病理學 骨骼與代謝疾病]': '骨質疏鬆、痛風、甲狀腺機能異常、糖尿病。',
    '[病理學 腎臟疾病]': '腎絲球腎炎、腎管坏死、腎臟結石、慢性腎臟病。',
    '[病理學 自體免疫疾病]': '自體抗體、自體免疫反應機制、常見自體免疫疾病。',
    '[病理學 骨骼與創傷]': '骨折分類、創傷修復過程、軟骨與骨骼疾病。',
    '[病理學 血液疾病]': '貧血、白血病、淋巴瘤、凝血障礙。',
    '[病理學 肝臟疾病]': '肝炎、肝硬化、肝衰竭、肝腫瘤。',
    '[病理學 感染性疾病]': '細菌性、病毒性、真菌性、寄生蟲性感染。',
    '[病理學 循環障礙]': '血栓、栓塞、休克、水腫。',
    '[病理學 藥理病理]': '藥物引起的病理變化、藥物毒性。',
    '[病理學 腎臟病理]': '腎臟疾病的病理變化與機制。',
    '[病理學 炎症與感染]': '炎症反應與感染性疾病的關聯。',
    '[藥理學 藥物治療]': '藥物治療原則：劑量、給藥途徑、療程。常見治療藥物分類。',
    '[藥理學 藥物作用機制]': '藥物與受體結合：激動劑、阻斷劑。藥物作用選擇性。',
    '[藥理學 藥物毒性與反應]': '副作用、過敏反應、毒性反應。藥物相互作用。',
    '[藥理學 精神科藥物]': '抗憂鬱劑（SSRI、SNRI）、抗焦慮劑、抗精神病劑、心境穩定劑。',
    '[藥理學 疫苗學]': '疫苗類型：活性減毒、不活化、次單位、mRNA。主動免疫 vs 被動免疫。',
    '[藥理學 內分泌藥物]': '甲狀腺藥物、胰島素、類固醇替代治療。',
    '[藥理學 心血管藥物]': '降壓藥（ACEI、ARB、CCB、利尿劑）、強心劑、抗心律不整藥、降血脂藥。',
    '[藥理學 糖尿病藥物]': '胰島素、雙胍類、磺醯脲類、DPP-4抑制劑、SGLT2抑制劑。',
    '[藥理學 呼吸系統藥物]': '支氣管擴張劑、類固醇、抗組織胺、止咳化痰藥。',
    '[藥理學 抗微生物藥]': '抗生素、抗病毒藥、抗真菌藥、抗寄生蟲藥。',
    '[藥理學 非類固醇抗發炎藥]': 'NSAIDs：抑制COX酵素，具止痛、退燒、抗發炎作用。副作用：胃潰瘍、腎臟毒性。',
    '[藥理學 抗癌藥物]': '細胞毒性化學治療、標靶治療、免疫治療。',
    '[藥理學 藥代動力學]': '藥物吸收、分佈、代謝、排泄（ADME）。生物利用度、半衰期。',
    '[藥理學 神經系統藥物]': '麻醉劑、鎮靜劑、抗癫痫藥、神經傳導物質調節劑。',
    '[藥理學 抗炎藥物]': '類固醇與非類固醇抗炎藥物比較。',
    '[藥理學 抗感染藥物]': '抗細菌、抗病毒、抗真菌、抗寄生蟲藥物。',
    '[藥理學 抗病毒藥物]': '抗病毒藥物：抗流感、抗B/C型肝炎、抗HIV。',
    '[藥理學 麻醉與鎮痛藥物]': '全身麻醉、局部麻醉、阿片類鎮痛劑。',
    '[藥理學 免疫抑制劑]': '器官移植用藥、自體免疫疾病用藥。',
    '[藥理學 骨骼與代謝藥物]': '骨質疏鬆治療、痛風藥物、電解質補充。',
    '[藥理學 止痛藥]': '鎮痛藥分類：非類固醇、阿片類、局部麻醉。',
    '[藥理學 抗生素]': 'β-內醯胺類、大環內酯類、四環素類、胺基糖苷類。',
    '[藥理學 一般藥理]': '藥理學基本概念：劑量-反應關係、治療指數。',
    '[藥理學 藥物動力學]': '藥物在體內的動態變化：吸收、分佈、代謝、排泄。',
    '[微生物學 病原體分類]': '細菌（革蘭氏陽性/陰性）、病毒、真菌、寄生蟲的基本分類與特徵。',
    '[微生物與免疫學 病原體與感染]': '常見病原微生物及其引起的感染疾病。',
    '[微生物學 抗藥性]': '抗藥性機制：酵素降解、靶點改變、外排幫浦、細胞壁通透性改變。',
    '[微生物學 重要傳染病]': '流感、結核病、登革熱、茲卡、COVID-19等重要傳染病。',
    '[微生物學 消毒與滅菌]': '消毒 vs 滅菌。物理方法（熱、輻射）、化學方法（酒精、漂白劑、過氧化氫）。',
    '[微生物學與免疫學 細菌學]': '細菌結構、培養、染色、鑑定。',
    '[微生物學與免疫學 寄生蟲學]': '原生動物、蠕蟲、節肢動物寄生蟲。',
    '[微生物學與免疫學 免疫學]': '免疫系統總覽：先天免疫與適應免疫。',
    '[免疫學 過敏反應]': '過敏反應四型：I型（立即型）、II型（細胞毒型）、III型（免疫複合體型）、IV型（遲發型）。',
    '[免疫學 免疫反應]': '免疫反應過程：抗原識別、活化、效應、記憶。',
    '[生物化學與細胞生物學 分子與細胞]': 'DNA、RNA、蛋白質合成。細胞信號傳導。',
    '[基礎醫學 一般]': '基礎醫學綜合知識。',
}

# Generate HTML
html_parts = []
html_parts.append("""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>護理師國家考試 — 110 基礎醫學 複習教材</title>
<style>
  :root {
    --bg: #fafbfc; --card: #ffffff; --text: #1a1a2e; --muted: #6c757d;
    --primary: #2563eb; --primary-light: #dbeafe; --success: #16a34a;
    --danger: #dc2626; --warning: #f59e0b; --border: #e5e7eb;
    --cat-a: #3b82f6; --cat-b: #10b981; --cat-c: #f59e0b;
    --cat-d: #8b5cf6; --cat-e: #ef4444; --cat-f: #ec4899;
    --cat-g: #14b8a6; --cat-z: #6b7280;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: "Noto Serif TC", "PMingLiU", serif; background: var(--bg); color: var(--text); line-height: 1.8; }
  
  /* Header */
  .header { background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%); color: white; padding: 2rem; text-align: center; }
  .header h1 { font-size: 1.8rem; margin-bottom: 0.3rem; }
  .header p { opacity: 0.85; font-size: 0.95rem; }
  .stats { display: flex; justify-content: center; gap: 1.5rem; margin-top: 1rem; flex-wrap: wrap; }
  .stat { background: rgba(255,255,255,0.15); padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.85rem; }
  
  /* TOC */
  .toc { max-width: 900px; margin: 1.5rem auto; padding: 1.5rem; background: var(--card); border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  .toc h2 { font-size: 1.2rem; margin-bottom: 0.8rem; color: var(--primary); }
  .toc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.5rem; }
  .toc-item { display: flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0.6rem; border-radius: 6px; text-decoration: none; color: var(--text); font-size: 0.9rem; transition: background 0.2s; }
  .toc-item:hover { background: var(--primary-light); }
  .toc-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
  .toc-count { margin-left: auto; font-size: 0.8rem; color: var(--muted); }
  
  /* Main content */
  .container { max-width: 900px; margin: 0 auto; padding: 0 1rem 3rem; }
  
  /* Category section */
  .category { margin: 2rem 0; }
  .category-header { display: flex; align-items: center; gap: 0.8rem; padding: 1rem 1.2rem; border-radius: 12px 12px 0 0; color: white; cursor: pointer; user-select: none; }
  .category-header h2 { font-size: 1.15rem; }
  .category-header .cat-count { font-size: 0.8rem; opacity: 0.85; }
  .cat-a .category-header { background: var(--cat-a); }
  .cat-b .category-header { background: var(--cat-b); }
  .cat-c .category-header { background: var(--cat-c); }
  .cat-d .category-header { background: var(--cat-d); }
  .cat-e .category-header { background: var(--cat-e); }
  .cat-f .category-header { background: var(--cat-f); }
  .cat-g .category-header { background: var(--cat-g); }
  .cat-z .category-header { background: var(--cat-z); }
  
  /* Topic section */
  .topic { border: 1px solid var(--border); border-top: none; }
  .topic-header { display: flex; align-items: center; justify-content: space-between; padding: 0.7rem 1.2rem; background: #f8fafc; cursor: pointer; border-bottom: 1px solid var(--border); transition: background 0.2s; }
  .topic-header:hover { background: #f1f5f9; }
  .topic-header h3 { font-size: 0.95rem; color: var(--text); }
  .topic-toggle { font-size: 0.8rem; color: var(--muted); transition: transform 0.3s; }
  .topic.open .topic-toggle { transform: rotate(180deg); }
  .topic-body { display: none; }
  .topic.open .topic-body { display: block; }
  
  /* Key points */
  .key-points { padding: 1rem 1.2rem; background: #fefce8; border-bottom: 1px solid #fde68a; font-size: 0.88rem; line-height: 1.9; }
  .key-points strong { color: #92400e; }
  
  /* Year groups */
  .year-group { padding: 0.8rem 1.2rem; border-bottom: 1px solid var(--border); }
  .year-label { font-size: 0.85rem; font-weight: bold; color: var(--primary); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.4rem; }
  .year-label::before { content: ''; width: 4px; height: 16px; background: var(--primary); border-radius: 2px; }
  
  /* Question card */
  .q-card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; margin: 0.5rem 0; }
  .q-stem { font-size: 0.92rem; margin-bottom: 0.6rem; font-weight: 500; }
  .q-options { display: grid; grid-template-columns: 1fr 1fr; gap: 0.3rem 1rem; margin-bottom: 0.6rem; }
  .q-opt { font-size: 0.85rem; padding: 0.2rem 0.5rem; border-radius: 4px; }
  .q-opt.correct { background: #dcfce7; color: #166534; font-weight: 600; }
  .q-opt.wrong { color: var(--muted); }
  .q-answer { font-size: 0.82rem; color: var(--success); font-weight: 600; }
  .q-explain { font-size: 0.82rem; color: var(--muted); margin-top: 0.3rem; font-style: italic; }
  .q-meta { font-size: 0.75rem; color: var(--muted); margin-bottom: 0.3rem; }
  
  /* Collapsible category body */
  .category-body { display: block; }
  .category.collapsed .category-body { display: none; }
  .category.collapsed .topic { display: none; }
  
  /* Back to top */
  .back-top { position: fixed; bottom: 1.5rem; right: 1.5rem; background: var(--primary); color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 8px rgba(0,0,0,0.2); opacity: 0; transition: opacity 0.3s; font-size: 1.2rem; }
  .back-top.show { opacity: 1; }
  
  /* Search */
  .search-box { max-width: 900px; margin: 1rem auto; padding: 0 1rem; }
  .search-box input { width: 100%; padding: 0.7rem 1rem; border: 1px solid var(--border); border-radius: 8px; font-size: 0.9rem; outline: none; transition: border-color 0.2s; }
  .search-box input:focus { border-color: var(--primary); }
  
  /* Print */
  @media print {
    .back-top, .search-box, .toc { display: none; }
    .category-header { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .topic-body { display: block !important; }
  }
  
  /* Responsive */
  @media (max-width: 600px) {
    .q-options { grid-template-columns: 1fr; }
    .stats { gap: 0.5rem; }
    .stat { font-size: 0.75rem; padding: 0.3rem 0.6rem; }
  }
</style>
</head>
<body>

<div class="header">
  <h1>護理師國家考試 — 110 基礎醫學</h1>
  <p>分類考題複習教材</p>
  <div class="stats">
""")

# Stats
total = len(entries)
years = sorted(set(get_year(e['file']) for e in entries))
num_cats = len(sorted_cats)
num_topics = len(topic_groups)
html_parts.append(f'<div class="stat">總題數：{total}</div>')
html_parts.append(f'<div class="stat">年份：{years[0]}〜{years[-1]}年</div>')
html_parts.append(f'<div class="stat">大分類：{num_cats}</div>')
html_parts.append(f'<div class="stat">細分類：{num_topics}</div>')

html_parts.append("""
  </div>
</div>

<div class="search-box">
  <input type="text" id="searchInput" placeholder="🔍 搜尋考題關鍵字..." oninput="filterQuestions()">
</div>

<nav class="toc" id="toc">
  <h2>📑 目錄</h2>
  <div class="toc-grid">
""")

# TOC
cat_colors = {'A': '#3b82f6', 'B': '#10b981', 'C': '#f59e0b', 'D': '#8b5cf6', 'E': '#ef4444', 'F': '#ec4899', 'G': '#14b8a6', 'Z': '#6b7280'}
for order, cat_name in sorted_cats:
    total_qs = sum(len(qs) for qs in cat_data[(order, cat_name)].values())
    html_parts.append(f'<a class="toc-item" href="#cat-{order}"><span class="toc-dot" style="background:{cat_colors[order]}"></span>{cat_name}<span class="toc-count">{total_qs}題</span></a>')

html_parts.append("""
  </div>
</nav>

<div class="container">
""")

# Content by category
for order, cat_name in sorted_cats:
    cat_class = f"cat-{order}"
    html_parts.append(f'<div class="category {cat_class}" id="cat-{order}">')
    html_parts.append(f'<div class="category-header" onclick="toggleCategory(this)">')
    
    total_qs = sum(len(qs) for qs in cat_data[(order, cat_name)].values())
    html_parts.append(f'<h2>{cat_name}</h2>')
    html_parts.append(f'<span class="cat-count">{len(cat_data[(order, cat_name)])} 細分類 · {total_qs} 題</span>')
    html_parts.append(f'<span style="margin-left:auto;font-size:0.8rem;">▼ 收合/展開</span>')
    html_parts.append('</div>')
    html_parts.append('<div class="category-body">')
    
    # Topics in this category
    for tag in sorted(cat_data[(order, cat_name)].keys()):
        qs = cat_data[(order, cat_name)][tag]
        html_parts.append(f'<div class="topic">')
        html_parts.append(f'<div class="topic-header" onclick="toggleTopic(this)">')
        html_parts.append(f'<h3>{tag} <span style="font-weight:normal;color:var(--muted);font-size:0.8rem;">({len(qs)}題)</span></h3>')
        html_parts.append('<span class="topic-toggle">▼</span>')
        html_parts.append('</div>')
        html_parts.append('<div class="topic-body">')
        
        # Key points
        kp = key_points.get(tag, '（考點整理待補）')
        html_parts.append(f'<div class="key-points"><strong>📌 考點重點：</strong>{kp}</div>')
        
        # Group by year
        year_qs = defaultdict(list)
        for q in qs:
            yr = get_year(q['file'])
            year_qs[yr].append(q)
        
        for yr in sorted(year_qs.keys()):
            html_parts.append(f'<div class="year-group">')
            html_parts.append(f'<div class="year-label">國{yr}年考題</div>')
            
            for q in year_qs[yr]:
                exam_label, _, _ = get_exam_label(q['file'])
                correct = q['answer'].strip().upper()
                
                stem_text = q.get("stem", "").replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
                html_parts.append(f'<div class="q-card" data-search="{stem_text}')
                
                # Meta
                html_parts.append(f'<div class="q-meta">題號 {q["question_id"]} · {exam_label}</div>')
                
                # Stem
                html_parts.append(f'<div class="q-stem">{q.get("stem", "(空題目)")}</div>')
                
                # Options
                opts = q.get('options', {})
                if opts:
                    html_parts.append('<div class="q-options">')
                    for letter in ['A', 'B', 'C', 'D']:
                        opt_text = opts.get(letter, '')
                        cls = 'q-opt correct' if letter == correct else 'q-opt wrong'
                        html_parts.append(f'<div class="{cls}">{letter}. {opt_text}</div>')
                    html_parts.append('</div>')
                
                # Answer
                html_parts.append(f'<div class="q-answer">✓ 答案：{correct}</div>')
                html_parts.append('<div class="q-explain">📝 解析：待補</div>')
                html_parts.append('</div>')
            
            html_parts.append('</div>')
        
        html_parts.append('</div>')
        html_parts.append('</div>')
    
    html_parts.append('</div>')
    html_parts.append('</div>')

html_parts.append("""
</div>

<a href="#" class="back-top" id="backTop" onclick="window.scrollTo({top:0,behavior:'smooth'});return false;">↑</a>

<script>
function toggleCategory(el) {
  el.parentElement.classList.toggle('collapsed');
}
function toggleTopic(el) {
  el.parentElement.classList.toggle('open');
}
// Back to top button
window.addEventListener('scroll', function() {
  document.getElementById('backTop').classList.toggle('show', window.scrollY > 400);
});
// Search filter
function filterQuestions() {
  const q = document.getElementById('searchInput').value.toLowerCase();
  document.querySelectorAll('.q-card').forEach(card => {
    const text = card.getAttribute('data-search').toLowerCase();
    card.style.display = text.includes(q) || q === '' ? '' : 'none';
  });
  // Auto-open topics when searching
  if (q) {
    document.querySelectorAll('.topic').forEach(t => t.classList.add('open'));
    document.querySelectorAll('.category').forEach(c => c.classList.remove('collapsed'));
  }
}
</script>
</body>
</html>
""")

# Write file
output_path = "/home/pascal/hermes-workspace/nursing_output/110_基礎醫學_教材.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(''.join(html_parts))

print(f"HTML generated: {output_path}")
import os
print(f"File size: {os.path.getsize(output_path)/1024:.0f}KB")
