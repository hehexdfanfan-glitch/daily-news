import json
import urllib.parse
import requests
import random
import re
from bs4 import BeautifulSoup

# --- 定義分類主題圖庫，確保「減少隨機性」與「提升關聯性」 ---
# 這些圖片是從 Unsplash 精選的專業攝影，分別對應不同情資類別
THEMED_IMAGES = {
    "mainstream": [
        "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?q=80&w=1000&auto=format&fit=crop", # 政治/議會
        "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?q=80&w=1000&auto=format&fit=crop", # 法律/文書
    ],
    "wildcard": [
        "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000&auto=format&fit=crop", # 新聞/報紙
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1000&auto=format&fit=crop", # 全球/科技/連網
    ],
    "finance": [
        "https://images.unsplash.com/photo-1611974717483-58da3c1c4ad6?q=80&w=1000&auto=format&fit=crop", # 股票/走勢
        "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?q=80&w=1000&auto=format&fit=crop", # 金錢/商務
    ],
    "tech": [
        "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1000&auto=format&fit=crop", # 電子/晶片
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=1000&auto=format&fit=crop", # 網路安全/AI
    ]
}

def get_best_fallback(section_key, original_title):
    """根據區塊獲取對應的主題圖"""
    # 映射區塊到主題
    mapping = {
        "mainstream_topics": "mainstream",
        "wildcard_topics": "wildcard",
        "business_finance_taiwan": "finance",
        "business_finance_global": "finance"
    }
    
    # 如果標題包含特定關鍵字，則微調主題
    title_low = original_title.lower()
    if any(k in title_low for k in ["chip", "ai", "tech", "semiconductor", "robot"]):
        theme = "tech"
    else:
        theme = mapping.get(section_key, "wildcard")
    
    # 從該主題中選出一張圖（為了減少隨機性，我們可以根據標題長度固定選擇其中一張）
    images = THEMED_IMAGES.get(theme, THEMED_IMAGES["wildcard"])
    idx = len(original_title) % len(images)
    return images[idx]

def get_real_news_image(url):
    """進階偵蒐：針對新聞網站優化"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Referer': 'https://www.google.com/'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. 優先掃描 Meta 標籤
        for selector in ['meta[property="og:image"]', 'meta[name="twitter:image"]', 'meta[property="twitter:image"]']:
            tag = soup.select_one(selector)
            if tag and tag.get('content'):
                return urllib.parse.urljoin(url, tag['content'])

        # 2. 掃描 JSON-LD
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                ld_data = json.loads(script.string)
                def extract_img(obj):
                    if isinstance(obj, dict):
                        if 'image' in obj:
                            img = obj['image']
                            return img.get('url') if isinstance(img, dict) else (img[0] if isinstance(img, list) else img)
                        for v in obj.values():
                            res = extract_img(v)
                            if res: return res
                    return None
                res = extract_img(ld_data)
                if res: return res
            except: continue

        # 3. 掃描內文關鍵區域的大圖
        article = soup.find('article') or soup.find('main')
        if article:
            for img in article.find_all('img'):
                # 檢查 srcset (通常包含更高解析度的圖)
                srcset = img.get('srcset')
                if srcset:
                    # 取第一個（通常是最小的，但也是最安全的）或解析出最大的
                    best_src = srcset.split(',')[0].split(' ')[0]
                    if 'http' in best_src: return best_src
                
                # 檢查 data-src (Lazy Load)
                src = img.get('data-src') or img.get('src')
                if src and not any(x in src.lower() for x in ['logo', 'icon', 'ad', 'pixel']):
                    if src.startswith('http'): return src
                    return urllib.parse.urljoin(url, src)

    except Exception as e:
        print(f"    ⚠️ 請求失敗: {e}")
    
    return None

def main():
    try:
        with open("raw_intelligence.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ 錯誤：找不到 raw_intelligence.json")
        return

    print("📸 Step 2: 啟動精準偵蒐模式...")
    
    sections = ['mainstream_topics', 'wildcard_topics', 'business_finance_taiwan', 'business_finance_global']
    
    for sec_key in sections:
        section = data.get(sec_key)
        if not section: continue
        for topic in section.get('topics', []):
            for article in topic.get('articles', []):
                print(f"  🔍 偵蒐: {article['front_title'][:15]}...")
                
                # 嘗試抓取真實圖片
                real_img = get_real_news_image(article['source_url'])
                
                if real_img:
                    article['image_url'] = real_img
                    print(f"    ✅ 成功獲取原圖")
                else:
                    # 根據區塊屬性分配「主題相關」的備案圖
                    fallback_img = get_best_fallback(sec_key, article['original_title'])
                    article['image_url'] = fallback_img
                    print(f"    🔄 使用主題匹配圖 ({fallback_img.split('/')[-1][:10]}...)")

    with open("enriched_intelligence.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print("\n✅ Step 2 更新完成！資料已存入 enriched_intelligence.json")

if __name__ == "__main__":
    main()
