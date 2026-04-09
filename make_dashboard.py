import os
import sys
import json
import urllib.parse
import requests
import random
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# ==========================================
# 0. 輔助工具：爬取網頁縮圖
# ==========================================
def get_og_image(url, title="news"):
    """嘗試從 URL 中多個標籤抓取縮圖，失敗則回傳具隨機性的占位圖"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 檢查多個常見標籤
            for selector in ['meta[property="og:image"]', 'meta[name="twitter:image"]', 'meta[itemprop="image"]']:
                tag = soup.select_one(selector)
                if tag and tag.get('content'):
                    img_url = tag['content']
                    if not img_url.startswith('http'):
                        img_url = urllib.parse.urljoin(url, img_url)
                    return img_url
    except Exception as e:
        print(f"⚠️ 無法抓取圖片 ({url}): {e}")
    
    # 如果抓不到，回傳一個具備隨機性的背景圖
    random_id = random.randint(1, 1000)
    return f"https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1000&auto=format&fit=crop&sig={random_id}"

# ==========================================
# 1. 定義嚴格的 JSON 結構 (使用 Pydantic)
# ==========================================
class Article(BaseModel):
    article_id: str = Field(description="文章的唯一ID，例如 main_t1_a1")
    source_tag: str = Field(description="來源媒體標籤，例如 [Fox News]")
    front_title: str = Field(description="顯示在卡片正面的短標題，必須為繁體中文")
    back_title: str = Field(description="顯示在卡片背面的短標題，必須為繁體中文")
    back_summary: str = Field(description="文章的深度摘要，約180字，必須為繁體中文")
    original_title: str = Field(description="最原始的網頁文章標題原文，用於搜尋溯源")
    source_url: str = Field(description="文章的原始 URL")
    image_url: str = Field(default="", description="文章的縮圖 URL (將由後端爬取補上)")

class Topic(BaseModel):
    topic_id: str = Field(description="主題的唯一ID，例如 main_01")
    risk_badge: str = Field(description="風險標籤的 CSS class，例如 bg-high, bg-med, bg-low, bg-info, bg-alert")
    badge_text: str = Field(description="風險標籤上的文字，例如 Risk: Critical, Trend: AI Race，必須為繁體中文")
    topic_title: str = Field(description="主題的大標題，必須為繁體中文")
    risk_reason: str = Field(description="一句話解釋為何重要，必須為繁體中文")
    topic_summary: str = Field(description="該主題的總結分析，必須為繁體中文")
    global_search_url: str = Field(description="追蹤該主題的 Google News 搜尋網址")
    articles: list[Article] = Field(description="該主題下的文章列表")

class Section(BaseModel):
    section_title: str = Field(description="區段的標題，例如 主流議題 // Mainstream Topics")
    topics: list[Topic] = Field(description="該區段下的主題列表")

class DashboardData(BaseModel):
    date_today: str = Field(description="今天的日期，格式 YYYY-MM-DD")
    time_now: str = Field(description="現在的時間，格式 HH:MM:SS CST")
    mainstream_topics: Section = Field(description="5個主流議題，每個包含3篇文章")
    wildcard_topics: Section = Field(description="3個潛在冷門議題，每個包含3篇文章")
    business_finance_taiwan: Section = Field(description="1個台灣財經主題，包含6篇文章")
    business_finance_global: Section = Field(description="1個國際財經主題，包含6篇文章")

# ==========================================
# 2. 核心執行邏輯
# ==========================================
def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ 錯誤：找不到 GEMINI_API_KEY 環境變數！")
        sys.exit(1)

    print("🌐 正在與 Gemini 總部連線，強制要求繁體中文結構化 JSON 輸出...")
    client = genai.Client(api_key=api_key)

    prompt = """
    請生成全球戰略情報儀表板的最新數據。所有顯示用的文字欄位（標題、摘要、分析、標籤文字）必須統一使用「繁體中文」。
    包含4大區塊：
    1. 主流議題（5個主題，如美伊衝突、俄烏、台海等，各3篇文章）。
    2. 潛在重大/冷門議題（主動挑選3個全新主題，各3篇文章）。
    3. 台灣商業與金融趨勢（近24小時內，1個主題，6篇文章）。
    4. 國際商業與金融趨勢（近24小時內，1個主題，6篇文章）。
    
    總共36篇深度情報。每篇文章摘要約180字。
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
            print("❌ 錯誤：API 回傳內容為空。")
            return

        dashboard_data = json.loads(response.text)
        
        print("📸 正在啟動情報偵察衛星，抓取新聞縮圖...")
        for section_key in ['mainstream_topics', 'wildcard_topics', 'business_finance_taiwan', 'business_finance_global']:
            section = dashboard_data.get(section_key)
            if not section: continue
            
            topics = section.get('topics', [])
            for topic in topics:
                for article in topic.get('articles', []):
                    article['image_url'] = get_og_image(article['source_url'], article['front_title'])
        
        build_html(dashboard_data)
        
    except Exception as e:
        print(f"❌ 獲取情報時發生錯誤：{e}")

# ==========================================
# 3. 將 JSON 塞入 HTML 模板的組裝引擎
# ==========================================
def build_html(data):
    print("🔨 正在將 JSON 數據映射至 HTML 模板...")
    
    try:
        with open("template.html", "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        print("❌ 找不到 template.html 檔案。")
        sys.exit(1)

    html = html.replace("{{DATE_TODAY}}", data["date_today"])
    html = html.replace("{{TIME_NOW}}", data["time_now"])

    # 填充 Section
    def fill_section(html_content, section_data, prefix, topic_count):
        html_content = html_content.replace("{{" + prefix + "_TITLE}}", section_data["section_title"])
        for i, topic in enumerate(section_data["topics"], start=1):
            if i > topic_count: break
            t_p = f"{prefix}_T{i}"
            html_content = html_content.replace("{{" + t_p + "_BADGE}}", topic["risk_badge"])
            html_content = html_content.replace("{{" + t_p + "_BADGE_TEXT}}", topic["badge_text"])
            html_content = html_content.replace("{{" + t_p + "_TITLE}}", topic["topic_title"])
            html_content = html_content.replace("{{" + t_p + "_REASON}}", topic["risk_reason"])
            html_content = html_content.replace("{{" + t_p + "_SUMMARY}}", topic["topic_summary"])
            html_content = html_content.replace("{{" + t_p + "_GLOBAL_SEARCH}}", topic["global_search_url"])
            
            for j, article in enumerate(topic["articles"], start=1):
                a_p = f"{t_p}_A{j}"
                html_content = html_content.replace("{{" + a_p + "_TAG}}", article["source_tag"])
                html_content = html_content.replace("{{" + a_p + "_F_TITLE}}", article["front_title"])
                html_content = html_content.replace("{{" + a_p + "_B_TITLE}}", article["back_title"])
                html_content = html_content.replace("{{" + a_p + "_B_SUM}}", article["back_summary"])
                html_content = html_content.replace("{{" + a_p + "_O_TITLE}}", article["original_title"])
                html_content = html_content.replace("{{" + a_p + "_URL}}", article["source_url"])
                html_content = html_content.replace("{{" + a_p + "_IMG}}", article.get("image_url", ""))
                html_content = html_content.replace("{{" + a_p + "_SEARCH_QUERY}}", urllib.parse.quote(article["original_title"]))
        return html_content

    html = fill_section(html, data["mainstream_topics"], "MAIN", 5)
    html = fill_section(html, data["wildcard_topics"], "WILD", 3)

    # 填充財經
    def fill_finance(html_content, section_data, prefix):
        topic = section_data["topics"][0] if section_data.get("topics") else section_data
        html_content = html_content.replace("{{" + prefix + "_BADGE}}", topic.get("risk_badge", "bg-info"))
        html_content = html_content.replace("{{" + prefix + "_BADGE_TEXT}}", topic.get("badge_text", ""))
        html_content = html_content.replace("{{" + prefix + "_TITLE}}", topic.get("topic_title", ""))
        html_content = html_content.replace("{{" + prefix + "_REASON}}", topic.get("risk_reason", ""))
        html_content = html_content.replace("{{" + prefix + "_SUMMARY}}", topic.get("topic_summary", ""))
        html_content = html_content.replace("{{" + prefix + "_GLOBAL_SEARCH}}", topic.get("global_search_url", ""))
        
        for j, article in enumerate(topic.get("articles", []), start=1):
            if j > 6: break
            a_p = f"{prefix}_A{j}"
            html_content = html_content.replace("{{" + a_p + "_TAG}}", article["source_tag"])
            html_content = html_content.replace("{{" + a_p + "_F_TITLE}}", article["front_title"])
            html_content = html_content.replace("{{" + a_p + "_B_TITLE}}", article["back_title"])
            html_content = html_content.replace("{{" + a_p + "_B_SUM}}", article["back_summary"])
            html_content = html_content.replace("{{" + a_p + "_O_TITLE}}", article["original_title"])
            html_content = html_content.replace("{{" + a_p + "_URL}}", article["source_url"])
            html_content = html_content.replace("{{" + a_p + "_IMG}}", article.get("image_url", ""))
            html_content = html_content.replace("{{" + a_p + "_SEARCH_QUERY}}", urllib.parse.quote(article["original_title"]))
        return html_content

    html = fill_finance(html, data["business_finance_taiwan"], "FIN_TW")
    html = fill_finance(html, data["business_finance_global"], "FIN_GL")

    output_filename = "daily_dashboard_rendered.html"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"✅ 更新完成！輸出檔案：{output_filename}")

if __name__ == "__main__":
    main()
