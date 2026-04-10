# 功能文檔：資料儲存與結構化管理

## 1. SQLite 架構
系統棄用單一 JSON 儲存，轉向關聯式資料庫 `intelligence.db`。

### 資料表結構
*   **`topics` 表**：
    *   `id`: 主鍵
    *   `date`: 情報日期 (YYYY-MM-DD)
    *   `topic_title`: 議題名稱
    *   `risk_reason`: 戰略風險分析
    *   `topic_summary`: 議題深度總結
*   **`articles` 表**：
    *   `id`: 主鍵
    *   `topic_id`: 外鍵 (關聯至 `topics.id`)
    *   `source_tag`: 來源媒體名稱
    *   `front_title`: 卡片標題
    *   `source_url`: 原始文章連結
    *   `image_url`: 抓取到的縮圖連結

## 2. 自動化存檔流程
在 `step4_archive.py` 執行時：
1. **結構化寫入**：將 `enriched_intelligence.json` 的內容解析並持久化至 SQLite。
2. **資料庫完整性**：每次存檔前自動執行 `init_db` 以確保 Schema 正確。
3. **長期追蹤**：情資一旦寫入 `intelligence.db`，即可供 Phase 3 的趨勢分析模組調用。
