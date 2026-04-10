import os
import sys
import json
import time
from datetime import datetime, timedelta, timezone
from google import genai
from google.genai import types
from models import DashboardData

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ 錯誤：找不到 GEMINI_API_KEY")
        sys.exit(1)

    print("🌐 Step 1: 正在與 Gemini 總部連線生成情報...")
    client = genai.Client(api_key=api_key)

    # 手動生成當前日期與時間 (台灣時間 UTC+8)
    tz_taiwan = timezone(timedelta(hours=8))
    now = datetime.now(tz_taiwan)
    date_today = now.strftime("%Y-%m-%d")
    time_now = now.strftime("%H:%M:%S CST")

    # 讀取固定的 5 個主流議題
    try:
        with open("topics.json", "r", encoding="utf-8") as f:
            fixed_topics = json.load(f)
    except FileNotFoundError:
        fixed_topics = ["美中科技戰", "俄烏戰爭", "台海局勢", "AI 發展", "全球通膨"]

    prompt = f"""
    今天是 {date_today}，現在時間是 {time_now} (UTC+8)。
    你是一名配備「實時搜尋能力」的高級戰略情報分析師。

    ### 任務指令：
    請利用 Google Search 工具，針對以下主題搜尋並產出最新的全球情報。

    ### 嚴格時效與內容要求：
    1. **財金資訊 (Business & Finance)**：必須嚴格限制在 **{time_now} 往前推 24 小時內** 發表的文章。
    2. **主流與潛在議題 (Strategic Intelligence)**：必須限制在 **{time_now} 往前推 48 小時內** 發表的文章。
    3. **真實性驗證**：
       - `source_url` 必須是搜尋結果中真實、可點擊的原文連結。
       - `original_title` 必須與原文完全一致，嚴禁編造。
       - 如果某個主題在規定時間內沒有足夠的新鮮資訊，請選擇該主題下最接近「今日」的重大進展，並在摘要中說明。

    ### 主題架構：
    1. 主流議題（必須包含）：{', '.join(fixed_topics)}。每個主題 3 篇文章。
    2. 潛在重大議題：主動搜尋 3 個「今日」最受關注的非主流主題，各 3 篇文章。
    3. 台灣/國際財金：各 1 個當日最火熱主題，各 6 篇文章（限 24H 內）。

    ### 輸出格式：
    必須符合 DashboardData Pydantic 模型，語言統一使用繁體中文（Original Title 除外）。
    """

    while True:
        try:
            # 啟用 Google Search 搜尋工具
            search_tool = types.Tool(google_search=types.GoogleSearch())

            response = client.models.generate_content(
                model='models/gemini-3.1-flash-lite-preview', # 切換至 3.1 預覽版，通常具備獨立額度
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[search_tool],
                    response_mime_type="application/json",
                    response_schema=DashboardData,
                ),
            )


            
            if not response.text:
                print("⚠️ API 回傳空內容，3 秒後重試...")
                time.sleep(3)
                continue

            data = json.loads(response.text)
            break # 成功獲取資料，跳出循環

        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "Service Unavailable" in error_msg:
                print("🚧 Gemini 總部暫時通訊中斷 (503)，10 秒後重新連線...")
                time.sleep(10)
            elif "429" in error_msg or "Quota" in error_msg:
                print("❌ 達到 API 配額上限 (429)，請檢查 Google AI Studio 剩餘額度。")
                sys.exit(1) # 直接退出，不再重試
            else:
                print(f"❌ Step 1 發生非預期錯誤：{e}")
                sys.exit(1)

    # 強制覆蓋為真實的日期與時間
    data["date_today"] = date_today
    data["time_now"] = time_now
    
    with open("raw_intelligence.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ Step 1 完成！當前時間：{date_today} {time_now}")

if __name__ == "__main__":
    main()
