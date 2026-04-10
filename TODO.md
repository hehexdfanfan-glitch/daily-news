# 全自動全球戰略情報儀表板 - 開發待辦清單 (TODO)

## Phase 1: 基礎架構與自動化 (Completed)
- [x] **建立 GitHub Actions 工作流**：設定每天 01:00 (UTC) 與 07:00 (UTC) 執行。
- [x] **環境變數設定**：在 GitHub Repository Secrets 中配置 `GEMINI_API_KEY`。
- [x] **自動 Push 機制**：自動將生成的 HTML commit 並 push 到 `gh-pages` 分支。
- [x] **核心生成 (Step 1)**：每日產出 36 篇繁中深度摘要。
- [x] **精準偵蒐 (Step 2)**：爬蟲支援 JSON-LD 與分類圖庫備案。
- [x] **歷史存檔 (Step 4)**：自動將每日情報存檔為 TXT 供長期趨勢分析。

## Phase 2: 視覺革命與資料庫導入 (Completed)
- [x] **導入 Jinja2 模板引擎**：取代僵化的字串替換，支持動態循環渲染。
- [x] **視覺設計升級 (CSS)**：引入玻璃擬態 (Glassmorphism)、現代字體排版與移動端 RWD。
- [x] **SQLite 資料庫整合**：建立 `database.py` 並將情資存入 `intelligence.db`。
- [x] **流程解耦優化**：重構 `step3_render.py` 以支援更靈活的模板開發。
- [x] **依賴項更新**：在 `deploy.yml` 中新增 `jinja2` 支持。

## Phase 3: 趨勢分析與多模態增強 (Pending)
- [ ] **互動式趨勢看板**：利用 SQLite 資料展示特定議題的演進時間軸。
- [ ] **多模態偵蒐**：評估利用 Gemini Vision 分析新聞原圖內容，提升摘要精準度。
- [ ] **GitHub Issue 深度互動**：優化週一主題建議報告的確認機制，實現自動化更新 `topics.json`。
- [ ] **搜尋功能**：在儀表板前端加入簡易的歷史情資檢索。

---
*註：此清單將隨開發進度持續更新。*
