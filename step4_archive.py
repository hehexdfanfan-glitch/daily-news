import os
import re
from bs4 import BeautifulSoup
from datetime import datetime

def archive_current_dashboard():
    target_file = "daily_dashboard_rendered.html"
    archive_dir = "archive"
    
    if not os.path.exists(target_file):
        print("ℹ️ 找不到現有的報告檔案，跳過存檔。")
        return

    print(f"📦 Step 4: 正在提取舊報告摘要並存檔...")
    
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 1. 提取日期 (從 HTML 中的 DATE: YYYY-MM-DD 結構中尋找)
        date_match = re.search(r"DATE: (\d{4}-\d{2}-\d{2})", html_content)
        if date_match:
            report_date = date_match.group(1)
        else:
            report_date = datetime.now().strftime("%Y-%m-%d")
            
        # 2. 建立存檔目錄
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)
            
        archive_path = os.path.join(archive_dir, f"{report_date}.txt")
        
        # 3. 提取所有的情報標題、摘要、來源標題與連結
        with open(archive_path, "w", encoding="utf-8") as out:
            out.write(f"=== 全球戰略情報存檔 [{report_date}] ===\n\n")
            
            # 遍歷所有的主題卡片
            topics = soup.find_all("div", class_="topic-card")
            for topic in topics:
                title = topic.find("h2", class_="topic-title")
                summary = topic.find("p", class_="summary-text")
                if title and summary:
                    out.write(f"📌 主題: {title.get_text(strip=True)}\n")
                    out.write(f"📝 深度摘要: {summary.get_text(strip=True)}\n")
                    out.write("🔗 來源情資:\n")
                    
                    # 尋找該主題下的所有來源連結與原始標題
                    # 根據模板，來源連結位於 class="btn-link" 的 <a> 標籤，原始標題在 data-original-title 屬性
                    sources = topic.find_all("a", class_="btn-link", href=True)
                    for i, source in enumerate(sources, start=1):
                        # 排除帶有 "alt" class 的搜尋按鈕，只抓取 "閱讀原文" 按鈕
                        if "alt" not in source.get("class", []):
                            # 嘗試從同級的搜尋按鈕抓取原始標題 (或從資料庫/JSON 結構推斷，但這裡以解析 HTML 為主)
                            # 在我們的模板中，搜尋按鈕就在閱讀原文按鈕旁邊
                            search_btn = source.find_previous_sibling("a", class_="alt")
                            original_title = search_btn.get("data-original-title") if search_btn else "未知原文標題"
                            
                            out.write(f"   {i}. [{original_title}]({source['href']})\n")
                            
                    out.write("-" * 50 + "\n\n")
            
        print(f"✅ 存檔完成！檔案位置：{archive_path}")
        
    except Exception as e:
        print(f"❌ 存檔失敗：{e}")

if __name__ == "__main__":
    archive_current_dashboard()
