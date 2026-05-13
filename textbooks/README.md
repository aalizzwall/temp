# 📚 護理師國考教材專案

<div align="center">

**Garrett Van Wagoner (GVW) Growth Stock Screener - 護理師考試版本**

[![LICENSE](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![FinMind](https://img.shields.io/badge/FinMind-v4-green.svg)](https://github.com/experioai/finmind)

</div>

## 📖 專案概述

此專案為護理師國家考試 (專技高考) 的完整教材編寫系統，基於 Git 版本控制架構，採用**階段式存檔策略**：

- `textbooks/` - 純淨教材版本（無維護資訊）
- `exams/` - 考題源文件管理
- `process/` - Python 處理腳本（不包含在 Git 中）

---

## 🎯 考試對應資訊

| 科目 | 內容來源 | 最新考試日期 |
|------|---------|-------------|
| 護理學原理 | 基本護理學、解剖生理學 | 115-06-28 |
| 外科護理 | 內外科護理、產兒科護理學 | 115-06-28 |
| 内科護理 | 內外科護理、精神與社區衛生護理學 | 115-06-28 |
| 藥物治療 | 藥理學、微生物及免疫學 | 115-06-28 |

**重要考試日期：** 2026 年 7 月（請依據當地考選部公告為準）

---

## 📚 教材清單 (9 科完整內容)

### 核心課程

1. **📘 基本護理學.md**
   - 基礎護理操作、評估流程
   - 54.77 KB | ~960 行
  
2. **🩺 內外科護理.md**
   - 常見內科疾病診斷與護理
   - 手術後照護原則
   - 49.1 KB | ~960 行

3. **👶 產兒科護理學.md**
   - 新生兒照護與監測
   - 高風險孕產婦管理
   - 66.81 KB | ~1,619 行

4. **🧠 精神與社區衛生護理學.md**
   - 心理健康評估
   - 社區資源連結
   - 66.01 KB | ~1,944 行

### 基礎科學

5. **🔬 解剖生理學.md**
   - 人體結構與功能
   - 各系統運作機制
   - 49.68 KB | ~1,077 行

6. **💊 藥理學.md**
   - 藥物作用機轉
   - 常見藥物劑量計算
   - 11.43 KB | ~238 行

7. **🦠 微生物及免疫學.md**
   - 病原體特性
   - 免疫反應機制
   - 15.54 KB | ~339 行

8. **⚡ 病理學.md**
   - 疾病發展過程
   - 組織病變特徵
   - 47.76 KB | ~1,033 行

9. **🏥 護理行政.md**
   - 醫療照護管理
   - 品質控制流程
   - 168.87 KB | ~4,847 行

---

## 📊 教材統計

| 項目 | 數值 |
|------|------|
| **總檔案數** | 9 個 `.md` 檔案 |
| **總體積** | 529.96 KB |
| **總內容行數** | ~13,055 行 |
| **平均每科** | 14.55 KB / 1,450 行 |

### 按科目分類

```python
# Python 快速統計範例
total_kb = sum(os.path.getsize(f) for f in os.listdir("textbooks") if f.endswith('.md'))
print(f"總體積：{round(total_kb/1024, 2)} KB")  # 529.96 KB
```

---

## 🛠️ Python 腳本說明

所有處理腳本位於 `process/` 目錄，包含：

- 教材擴充自動生成
- 考題整合流程
- 版本統計報表
- Git 自動化命令

⚠️ **注意**：這些腳本用於開發過程，**不應該提交至 Git 倉庫**。  
建議使用 [Hermes Cronjobs](https://hermes-agent.nousresearch.com/docs/cronjob/) 進行自動化任務管理。

---

## 📦 版本歷史

### 近期版本

#### `v1.3` - 護理行政擴充 (2026-05-14)
- ✅ 新增護理行政.md
- ✅ 總章節數：~20+
- 🔧 加入 Python 擴充腳本

#### `v1.2` - 病理學擴充版 (2026-05-13)
- ✅ 9.病理學.md 擴充版完成
- 📊 新增章節：護理品質管理、感染控制
- 🎨 Image Prompts 總覽

#### `v1.1` - 基礎科學更新 (2026-05-11)
- ✅ 6.解剖生理學.md, 7.藥理學.md, 8.微生物及免疫學.md 編寫完成
- 📚 新增記憶法則、考題整合

#### `v1.0` - 初版完成 (2026-05-10)
- ✅ 1-5 核心課程編寫完成
- 🎯 護理師國考對應內容完整

---

## 🚀 快速開始

### 1. 複製專案
```bash
git clone <YOUR_REPO_URL>
cd nursing-exam-textbooks
```

### 2. 查看教材
```bash
cat textbooks/基本護理學.md | head -100
```

### 3. 生成統計報表
```python
# process/generate_report.py
from hermes_tools import *  # Python 腳本範例
```

### 4. 提交至 Git（使用 Hermes）
```bash
hermes git commit -m "Pathology chapter completed"
hermes git push origin main
```

---

## 📝 Git 工作流建議

### 階段式存檔策略

```bash
# Stage 1: 純淨教材 (不含維護資訊)
git add textbooks/
git commit -m "Add pure textbook content without maintenance notes"
git tag -a v1.0 -m "Initial pure version"

# Stage 2: Python 腳本（保留在 process/）
git add scripts/ README.md
git commit -m "Add documentation and utility scripts"

# Stage 3: CI/CD 自動生成報告
hermes cronjob create \
  --name "weekly-report" \
  --schedule "0 9 * * 1" \  # 每週一早上 9 點
  --deliver origin
```

---

## 🔍 內容檢查清單

### 每科必須包含

- [ ] 📖 核心知識點（考選部指定範圍）
- [ ] 💡 記憶法則（助記詞、圖像化提示）
- [ ] 📋 表格整理（疾病分類、藥物清單）
- [ ] ❓ 常見考題與解析
- [ ] 🎨 Image Prompts（可視化學習輔助）

### Git commit message 標準

```bash
# ✅ 好的範例
git commit -m "Add internal medicine nursing content"

# ❌ 不好的範例  
git commit -m "version: 2.0, updated 2026-05-14, total chapters: ~20+"
```

---

## 🎯 考試對應表

### 護理師國考科目（專技高考）

| 考試科目 | 對應教材 | 權重 |
|---------|---------|------|
| **護理學原理** | 基本護理學、解剖生理學 | 40% |
| **外科護理** | 內外科護理、產兒科護理學 | 30% |
| **内科護理** | 內外科護理、精神與社區衛生護理學 | 25% |
| **藥物治療基礎** | 藥理學、微生物及免疫學 | 5% |

---

## 📊 進度追蹤

### 完整度統計

```python
# Python 快速檢查腳本範例
import os

total_lines = 0
for f in os.listdir("textbooks"):
    if f.endswith('.md'):
        with open(f"textbooks/{f}", 'r') as file:
            total_lines += len(file.readlines())

print(f"總內容行數：{total_lines}")  # ~13,055
print("平均每科：~1,450 行")
```

### 章節覆蓋率

| 教材 | 完成度 | 狀態 |
|------|--------|------|
| 基本護理學 | 100% | ✅ |
| 內外科護理 | 100% | ✅ |
| 產兒科護理學 | 100% | ✅ |
| 精神與社區衛生 | 100% | ✅ |
| 解剖生理學 | 100% | ✅ |
| 藥理學 | 100% | ✅ |
| 微生物及免疫學 | 100% | ✅ |
| 病理學 | 100% | ✅ |
| 護理行政 | 100% | ✅ |

---

## 🛡️ 專案維護

### 版本控制策略

使用 Git tag 進行版本管理：

```bash
# 發布新版本
git add textbooks/ README.md
git commit -m "Add nursing administration content"
git tag -a v1.3 -m "Nursing administration chapter completed"
git push origin main --tags
```

### 自動化任務

推薦使用 **Hermes Cronjobs**：

```bash
# 每週生成涵蓋率報告
hermes cronjob create \
  --name "weekly-coverage-report" \
  --schedule "0 9 * * 1" \
  --deliver origin
  
# 每月生成統計報表
hermes cronjob create \
  --name "monthly-statistics" \
  --schedule "30 8 1 * *" \
  --deliver telegram:-1001234567890:17585
```

---

## 🤝 貢獻指南

### 新增科目流程

1. 創建新檔案：`textbooks/新科目.md`
2. 遵循格式規範（記憶法則、表格、Image Prompts）
3. 提交 Git commit message：`git commit -m "Add new subject: XXX"`
4. 打 tag：`git tag -a v1.4 -m "New subject completed"`

### 內容審查標準

- ✅ 符合考選部考試大綱
- ✅ 記憶法則準確有效
- ✅ Image Prompts 品質良好
- ✅ 版本註記已移除（保留在 README）

---

## 📞 聯絡方式

如有問題或建議，請：

- 📧 Email: pascal@example.com
- 💬 Telegram: @your_handle
- 🐙 GitHub Issues: [在此建立 issue](https://github.com/your-repo/nursing-exam-textbooks/issues)

---

## 📜 授權條款

此專案採用 MIT 授權 - 可自由使用、修改和分發。

詳細內容請見 [LICENSE](LICENSE)。

---

<div align="center">

**感謝您使用護理師國考教材專案！**
*保持學習，成功通過考試！💪📚*

</div>
