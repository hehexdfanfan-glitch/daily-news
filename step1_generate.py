import os
import sys
import json
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

    prompt = """
    請生成全球戰略情報儀表板的最新數據。所有顯示用的文字欄位（標題、摘要、分析、標籤文字）必須統一使用「繁體中文」。
    包含 4 大區塊：
    1. 主流議題（5 個主題，如美伊衝突、俄烏、台海等，各 3 篇文章）。
    2. 潛在重大/冷門議題（主動挑選 3 個全新主題，各 3 篇文章）。
    3. 台灣商業與金融趨勢（近 24 小時內，1 個主題，6 篇文章）。
    4. 國際商業與金融趨勢（近 24 小時內，1 個主題，6 篇文章）。
    
    總共 36 篇深度情報。每篇文章摘要約 180 字。
    關鍵要求：
    - 必須抓取並保留每篇文章的「最原始網頁標題原文 (original_title)」，這部分維持原文（通常是英文）。
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

        # 驗證並儲存原始資料
        data = json.loads(response.text)
        with open("raw_intelligence.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print("✅ Step 1 完成！產出原始情報檔案：raw_intelligence.json")
        
    except Exception as e:
        print(f"❌ Step 1 失敗：{e}")

if __name__ == "__main__":
    main()
