import os
import json
from datetime import datetime
from database import init_db, save_dashboard_data

def archive_to_db():
    """從 JSON 檔案將情資結構化存入 SQLite 資料庫"""
    try:
        # 優先尋找經過 Crawl 補全的資料
        target_json = "enriched_intelligence.json"
        if not os.path.exists(target_json):
            target_json = "raw_intelligence.json"

        if not os.path.exists(target_json):
            print(f"ℹ️ 找不到情報來源 ({target_json})，跳過存檔。")
            return

        with open(target_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"📦 Step 4: 正在將 {target_json} 情資存入長期資料庫...")
        
        # 初始化資料庫 (確保 Table 結構正確)
        init_db()
        
        # 執行結構化寫入
        save_dashboard_data(data)
        
        print(f"✅ 資料庫存檔成功！當前存檔檔案：{target_json}")

    except Exception as e:
        print(f"❌ 資料庫存檔失敗：{e}")

if __name__ == "__main__":
    archive_to_db()
