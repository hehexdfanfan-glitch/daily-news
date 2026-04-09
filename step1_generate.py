import os
import sys
import json
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
        print("❌ 錯誤：找不到 topics.json")
        fixed_topics = ["美中科技戰", "俄烏戰爭", "台海局勢", "AI 發展", "全球通膨"]

    prompt = f"""
    請生成全球戰略情報儀表板的最新數據。所有顯示用的文字欄位（標題、摘要、分析、標籤文字）必須統一使用「繁體中文」。
    包含 4 大區塊：
    1. 主流議題（必須嚴格按照以下 5 個主題生成，每個主題 3 篇文章）：
       - {fixed_topics[0]}
       - {fixed_topics[1]}
       - {fixed_topics[2]}
       - {fixed_topics[3]}
       - {fixed_topics[4]}
    2. 潛在重大/冷門議題（主動挑選 3 個全新主題，各 3 篇文章）。
    3. 台灣商業與金融趨勢（1 個主題，6 篇文章）。
    4. 國際商業與金融趨勢（1 個主題，6 篇文章）。
    
    總共 36 篇深度情報。每篇文章摘要約 180 字。
    關鍵要求：
    - original_title 維持原文（通常是英文）。
    - 欄位 front_title, back_title, back_summary, badge_text, topic_title, risk_reason, topic_summary 必須為繁體中文。
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DashboardData,
            ),
        )
        
        if not response.text:
            print("❌ 錯誤：API 回傳空內容。")
            return

        data = json.loads(response.text)
        
        # 強制覆蓋為真實的日期與時間
        data["date_today"] = date_today
        data["time_now"] = time_now
        
        with open("raw_intelligence.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"✅ Step 1 完成！當前時間：{date_today} {time_now}")
        
    except Exception as e:
        print(f"❌ Step 1 失敗：{e}")

if __name__ == "__main__":
    main()
