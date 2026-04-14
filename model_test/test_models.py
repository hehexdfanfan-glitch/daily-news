import os
import sys

# 將專案根目錄加入系統路徑，以正確導入 models.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import time
from datetime import datetime, timedelta, timezone
from google import genai
from google.genai import types
from models import DashboardData

# 欲測試的「穩定型/經典型」模型清單
TEST_MODELS = [
    "gemini-2.0-flash",
    "gemini-pro-latest",   # 1.5 Pro 穩定版
    "gemini-flash-latest", # 1.5 Flash 穩定版
    "gemini-2.0-flash-lite"
]

def run_test():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ 錯誤：找不到 GEMINI_API_KEY")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    
    # 準備基本測試 Prompt
    prompt = """
    請利用 Google Search 搜尋今日最受關注的 3 個全球戰略情報主題，並產出情報。
    必須符合 DashboardData Pydantic 模型，語言統一使用繁體中文。
    """

    results = {}

    for model_id in TEST_MODELS:
        print(f"\n🚀 正在測試模型: {model_id}...")
        start_time = time.time()
        
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
                elapsed = round(time.time() - start_time, 2)
                print(f"✅ {model_id} 成功！耗時: {elapsed}s")
                
                # 儲存個別 JSON
                output_file = f"model_test/result_{model_id.replace('-', '_')}.json"
                data = json.loads(response.text)
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                
                results[model_id] = "SUCCESS"
            else:
                print(f"⚠️ {model_id} 回傳空內容。")
                results[model_id] = "EMPTY_CONTENT"

        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            print(f"❌ {model_id} 失敗 (耗時 {elapsed}s)")
            print(f"--- 原始錯誤訊息 ---")
            print(str(e))
            print(f"--------------------")
            results[model_id] = f"FAILED: {str(e)}"

    print("\n" + "="*50)
    print("📊 最終測試結果摘要:")
    for m, res in results.items():
        print(f"  - {m}: {res}")
    print("="*50)

if __name__ == "__main__":
    run_test()
