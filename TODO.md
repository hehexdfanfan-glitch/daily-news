# 專案進度追蹤 (Project Progress)

## Phase 2: 全面優化 (Completed)
- [x] **情資時效革命**：實作財金 24h / 戰略 48h 嚴格過濾機制。
- [x] **實時搜尋工具**：啟用 Gemini Grounding，消除 URL 幻覺與過時文章。
- [x] **架構極簡化**：移除 TXT 存檔，全面由 SQLite 接手結構化情資管理。
- [x] **渲染動態化**：Jinja2 模板導入，支援自適應佈局與美化設計。

## Phase 3: 深度分析與多模態 (Current Phase)
- [ ] **模型策略優化**：基於 2026/04 實測，升級為 `gemini-3.1-pro-preview` 並實作 Fallback 至 `gemini-3-flash-preview` 的容錯機制，解決 503 與 JSON 工具相容性問題。
- [ ] **歷史趨勢模組**：開發基於 SQLite 的 SQL 查詢邏輯，展示議題熱度演進時間軸。
- [ ] **高價值偵蒐 (Computer Use)**：針對反爬蟲媒體（Bloomberg, WSJ 等）導入視覺化自動擷取。
- [ ] **多模態增強**：利用 Vision 模型直接分析新聞原始圖像，提升摘要關聯性。
- [ ] **自動化閉環**：整合 Step 0 建議報告，實現主題自動更新機制。
