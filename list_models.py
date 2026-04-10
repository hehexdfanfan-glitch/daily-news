import os
import sys
from google import genai

def list_all_models():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ 錯誤：找不到 GEMINI_API_KEY 環境變數。")
        sys.exit(1)

    print("🔍 正在連線至 Google AI Studio 獲取可用模型清單...\n")
    client = genai.Client(api_key=api_key)

    try:
        # 直接獲取模型清單
        models = client.models.list()
        
        # 標題
        print(f"{'Model ID':<40} | {'JSON':<6} | {'Search':<8}")
        print("-" * 60)

        found_models = 0
        for m in models:
            # 放寬過濾條件，直接列出所有包含 "gemini" 字樣的模型
            if "gemini" in m.name.lower():
                found_models += 1
                
                # 嘗試判斷 JSON 支援 (Structured Output)
                # 較舊版本的 SDK 可能不支援，或是欄位名稱不同
                json_support = "✅" if hasattr(m, 'supported_mime_types') and "application/json" in m.supported_mime_types else "---"
                
                # 搜尋能力基本上在 Gemini 1.0/1.5/2.0 都支援
                search_support = "🚀"
                
                display_name = m.name.replace("models/", "")
                print(f"{display_name:<40} | {json_support:<6} | {search_support:<8}")

        if found_models == 0:
            print("⚠️ 警告：未找到任何 Gemini 模型。這可能是 API KEY 權限不足或是 SDK 回傳格式不符。")
            # 印出一個原始模型物件來除錯
            print("\n[Debug] 原始資料範例：")
            for m in client.models.list():
                print(vars(m))
                break

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")

if __name__ == "__main__":
    list_all_models()
