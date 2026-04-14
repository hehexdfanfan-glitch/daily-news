import os
import sys
import json
import time
from datetime import datetime, timedelta, timezone
from google import genai
from google.genai import types
from models import DashboardData

# 2026/04 調度金字塔 (Flagship -> Efficiency -> Stability -> Final Defense)
STRATEGIC_MODELS = [
    "gemini-3.1-pro-preview",
    "gemini-3-flash-preview",
    "gemini-pro-latest",
    "gemini-flash-latest"
]

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ 錯誤：找不到 GEMINI_API_KEY")
        sys.exit(1)

    print("🌐 Step 1: 正在連線至全自動情報偵蒐中心...")
    client = genai.Client(api_key=api_key)

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

    ### 主題架構：
    1. 主流議題（必須包含）：{', '.join(fixed_topics)}。每個主題 3 篇文章。
    2. 潛在重大議題：主動搜尋 3 個「今日」最受關注的非主流主題，各 3 篇文章。
    3. 台灣/國際財金：各 1 個當日最火熱主題，各 6 篇文章（限 24H 內）。

    ### 輸出格式：
    必須符合 DashboardData Pydantic 模型，語言統一使用繁體中文（Original Title 除外）。
    """

    success_data = None
    applied_model = "None"

    # 開始執行調度金字塔
    for model_id in STRATEGIC_MODELS:
        print(f"🚀 嘗試使用模型: {model_id}...")
        try:
            search_tool = types.Tool(google_search=types.GoogleSearch())
            
            response = client.models.generate_content(
                model=f"models/{model_id}",
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[search_tool],
                    response_mime_type="application/json",
                    response_schema=DashboardData,
                ),
            )

            if response.text:
                success_data = json.loads(response.text)
                applied_model = model_id
                print(f"✅ {model_id} 生成成功！")
                break # 成功即跳出
            else:
                print(f"⚠️ {model_id} 回傳內容為空，嘗試下一順位...")

        except Exception as e:
            error_msg = str(e)
            print(f"❌ {model_id} 發生錯誤：{error_msg[:100]}...")
            if "Quota" in error_msg or "429" in error_msg:
                print("⏳ 觸發配額限制，跳過此模型...")
            elif "503" in error_msg or "Unavailable" in error_msg:
                print("🚧 模型暫時不可用，嘗試備援方案...")
            else:
                print("🔍 非預期錯誤，進入 Fallback 流程...")
            continue # 嘗試下一個模型

    if not success_data:
        print("🚨 關鍵錯誤：所有模型均無法生成資料！")
        sys.exit(1)

    # 注入元數據
    success_data["date_today"] = date_today
    success_data["time_now"] = time_now
    success_data["generated_by"] = applied_model
    
    with open("raw_intelligence.json", "w", encoding="utf-8") as f:
        json.dump(success_data, f, ensure_ascii=False, indent=4)
    
    print(f"✨ Step 1 完成！使用模型：{applied_model}")

if __name__ == "__main__":
    main()
