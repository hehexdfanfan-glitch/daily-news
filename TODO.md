# 全自動全球戰略情報儀表板 - 開發待辦清單 (TODO)

## 1. 自動化排程 (Automation)
- [x] **建立 GitHub Actions 工作流**：設定每天 01:00 (UTC) 與 07:00 (UTC) 執行（對應台北時間 9:00 與 15:00）。
- [x] **環境變數設定**：在 GitHub Repository Secrets 中配置 `GEMINI_API_KEY`。
- [x] **自動 Push 機制**：執行完 `make_dashboard.py`（現已拆分為 step 1~3）後，自動將生成的 HTML commit 並 push 到 `gh-pages` 分支或主分支。

## 2. 圖片縮圖爬取 (Image Scraping)
- [x] **擴充 Pydantic 模型**：在 `Article` 模型中新增 `image_url` 欄位。
- [x] **整合爬蟲邏輯**：
    - [x] 方案 A：在 Python 中使用 `BeautifulSoup` 根據 `source_url` 抓取 `og:image`。
- [x] **更新模板注入**：修改 `make_dashboard.py`，將 `{{IMAGE_URL}}` 佔位符替換為實際抓到的連結。

## 3. 主題管理與推薦系統 (Topic Management)
- [ ] **持久化儲存**：建立 `topics.json` 用於存儲目前的 5 個固定主流議題。
- [ ] **週一推薦邏輯**：
    - [ ] 檢查當天是否為週一。
    - [ ] 若為週一，呼叫 Gemini 額外生成「主題建議報告」。
    - [ ] 建立互動機制（如 GitHub Issue 或簡易 Web 確認）供使用者決定是否更換。
- [ ] **更新 Prompt**：確保 API 呼叫時會參考 `topics.json` 中的固定主題。

## 4. GitHub Pages 部署與存檔 (Deployment & Archive)
- [ ] **部署設定**：確保 `index.html` 指向最新的 `daily_dashboard_rendered.html`。
- [ ] **存檔引擎 (Archive Engine)**：
    - [ ] 每次執行前，將舊的 `.html` 內容提取純文字摘要。
    - [ ] 將純文字存入 `archive/YYYY-MM-DD.txt` 或資料庫。
    - [ ] 提交存檔檔案至 GitHub。

---
*註：此清單將隨開發進度持續更新。*
