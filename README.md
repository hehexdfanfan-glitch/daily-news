# 全自動全球戰略情報儀表板 (Global Strategic Intelligence Dashboard)

本專案是一個基於 Gemini API 與 Python 構建的自動化情報分析系統，旨在為決策者提供具備實時性、準確性與長期溯源能力的全球戰略情資。

---

## 目錄
1. [專案概述](#專案概述)
2. [技術棧](#技術棧)
3. [快速啟動](#快速啟動)
4. [目錄結構](#目錄結構)
5. [詳細功能文檔](#詳細功能文檔)

---

## 專案概述
本系統每日定時（09:00, 15:00 UTC+8）執行，自動搜尋全球主流與潛在戰略議題。透過 Gemini 3.1/2.0 系列模型的實時搜尋能力 (Grounding)，系統能確保每一條情報均具備真實的來源連結，並嚴格遵守財金 24 小時、戰略 48 小時的時效約束。

## 技術棧
*   **核心引擎**: Google Gemini 2.0/3.1 系列模型
*   **後端語言**: Python 3.13
*   **資料儲存**: SQLite 3 (智慧存檔與結構化檢索)
*   **模板渲染**: Jinja2 (動態 HTML 佈局)
*   **自動化**: GitHub Actions (定時排程與自動部署)

## 快速啟動
在使用前，請確保已配置 `GEMINI_API_KEY` 環境變數。

```bash
# 安裝依賴
pip install -r requirements.txt

# 執行完整工作流
python step1_generate.py    # 生成情報
python step2_crawl.py       # 抓取縮圖
python step3_render.py      # 渲染頁面
python step4_archive.py     # 資料存檔
```

## 目錄結構
```text
C:\Users\royma\CLI\daily-static-site\
├── database.py            # SQLite 資料庫操作核心
├── intelligence.db        # 長期情資資料庫 (SQLite)
├── models.py              # Pydantic 資料模型定義
├── step1_generate.py      # 情報搜尋與生成引擎
├── step2_crawl.py         # 圖片偵蒐與爬蟲模組
├── step3_render.py        # Jinja2 模板渲染引擎
├── step4_archive.py       # 自動存檔與資料庫同步
├── template.html          # Jinja2 佈局模板
├── legacy_and_tools/      # 過時腳本與本地工具 (排除同步)
│   └── available_models.json  # 定期更新的模型清單 (核心配置參考)
└── TODO.md                # 研發進度追蹤
```

## 詳細功能文檔
*   [情報生成與搜尋策略](DOC_AI_STRATEGY.md)
*   [資料儲存與結構化管理](DOC_DATA_STORAGE.md)
*   [渲染引擎與存檔機制](DOC_RENDER_ARCHIVE.md)
