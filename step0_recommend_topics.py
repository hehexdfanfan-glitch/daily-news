import os
import sys
import json
from datetime import datetime, timedelta, timezone
from google import genai
from google.genai import types

def main():
    # 判斷今天是否為週一 (台灣時間 UTC+8)
    tz_taiwan = timezone(timedelta(hours=8))
    now = datetime.now(tz_taiwan)
    if now.weekday() != 0:
        print("ℹ️ 今天不是週一，跳過主題推薦檢查。")
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ 錯誤：找不到 GEMINI_API_KEY")
        sys.exit(1)

    print("🌐 Step 0: 正在呼叫 Gemini 生成「每週主題建議報告」...")
    client = genai.Client(api_key=api_key)

    try:
        with open("topics.json", "r", encoding="utf-8") as f:
            current_topics = json.load(f)
    except FileNotFoundError:
        current_topics = []

    prompt = f"""
    你是一名資深國際戰略與情報分析師。今天是 {now.strftime("%Y-%m-%d")}。
    我們目前的全球戰略情報儀表板固定追蹤以下 5 個主流議題：
    {', '.join(current_topics)}

    請檢視這 5 個議題是否仍然是當前全球最重要、最具影響力的焦點。
    請提出一份「每週主題建議報告」，包含：
    1. 對現有 5 個主題的簡短評價（是否該保留）。
    2. 建議的新增/替換主題（如果有的話，請說明替換理由；如果沒有，請說明維持現狀的理由）。
    
    請以繁體中文撰寫，格式為 Markdown，無需任何 Markdown 語法區塊標籤（如 ```markdown），直接輸出純文字內容即可。
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        if not response.text:
            print("❌ 錯誤：API 回傳空內容。")
            return

        with open("topic_recommendation.md", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print("✅ Step 0 完成！產出推薦報告：topic_recommendation.md")
        
    except Exception as e:
        print(f"❌ Step 0 失敗：{e}")

if __name__ == "__main__":
    main()
