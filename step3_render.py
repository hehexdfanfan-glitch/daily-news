import json
import urllib.parse
import sys

def build_html(data):
    try:
        with open("template.html", "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        print("❌ 找不到 template.html")
        sys.exit(1)

    html = html.replace("{{DATE_TODAY}}", data["date_today"])
    html = html.replace("{{TIME_NOW}}", data["time_now"])

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
    print(f"✅ Step 3 完成！最終報告輸出為：{output_filename}")

def main():
    # 優先嘗試 enriched (已爬取圖片) 的資料，否則用 raw
    for filename in ["enriched_intelligence.json", "raw_intelligence.json"]:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"🔨 Step 3: 正在讀取 {filename} 並繪製 HTML...")
                build_html(data)
                return
        except FileNotFoundError:
            continue
    print("❌ 錯誤：找不到任何 JSON 資料檔案，請先執行 step1 或 step2。")

if __name__ == "__main__":
    main()
