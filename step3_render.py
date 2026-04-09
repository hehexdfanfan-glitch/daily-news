import json, urllib.parse, sys

def fill_section(html, section_data, prefix, topic_count):
    html = html.replace("{{" + prefix + "_TITLE}}", section_data["section_title"])
    for i, topic in enumerate(section_data["topics"], start=1):
        if i > topic_count: break
        t_p = f"{prefix}_T{i}"
        html = html.replace("{{" + t_p + "_BADGE}}", topic["risk_badge"])
        html = html.replace("{{" + t_p + "_BADGE_TEXT}}", topic["badge_text"])
        html = html.replace("{{" + t_p + "_TITLE}}", topic["topic_title"])
        html = html.replace("{{" + t_p + "_REASON}}", topic["risk_reason"])
        html = html.replace("{{" + t_p + "_SUMMARY}}", topic["topic_summary"])
        html = html.replace("{{" + t_p + "_GLOBAL_SEARCH}}", topic["global_search_url"])
        for j, article in enumerate(topic["articles"], start=1):
            a_p = f"{t_p}_A{j}"
            html = html.replace("{{" + a_p + "_TAG}}", article["source_tag"])
            html = html.replace("{{" + a_p + "_F_TITLE}}", article["front_title"])
            html = html.replace("{{" + a_p + "_B_TITLE}}", article["back_title"])
            html = html.replace("{{" + a_p + "_B_SUM}}", article["back_summary"])
            html = html.replace("{{" + a_p + "_O_TITLE}}", article["original_title"])
            html = html.replace("{{" + a_p + "_URL}}", article["source_url"])
            html = html.replace("{{" + a_p + "_IMG}}", article.get("image_url", ""))
            html = html.replace("{{" + a_p + "_SEARCH_QUERY}}", urllib.parse.quote(article["original_title"]))
    return html

def fill_finance(html, section_data, prefix):
    topic = section_data["topics"][0] if section_data.get("topics") else section_data
    html = html.replace("{{" + prefix + "_BADGE}}", topic.get("risk_badge", "bg-info"))
    html = html.replace("{{" + prefix + "_BADGE_TEXT}}", topic.get("badge_text", ""))
    html = html.replace("{{" + prefix + "_TITLE}}", topic.get("topic_title", ""))
    html = html.replace("{{" + prefix + "_REASON}}", topic.get("risk_reason", ""))
    html = html.replace("{{" + prefix + "_SUMMARY}}", topic.get("topic_summary", ""))
    html = html.replace("{{" + prefix + "_GLOBAL_SEARCH}}", topic.get("global_search_url", ""))
    for j, article in enumerate(topic.get("articles", []), start=1):
        if j > 6: break
        a_p = f"{prefix}_A{j}"
        html = html.replace("{{" + a_p + "_TAG}}", article["source_tag"])
        html = html.replace("{{" + a_p + "_F_TITLE}}", article["front_title"])
        html = html.replace("{{" + a_p + "_B_TITLE}}", article["back_title"])
        html = html.replace("{{" + a_p + "_B_SUM}}", article["back_summary"])
        html = html.replace("{{" + a_p + "_O_TITLE}}", article["original_title"])
        html = html.replace("{{" + a_p + "_URL}}", article["source_url"])
        html = html.replace("{{" + a_p + "_IMG}}", article.get("image_url", ""))
        html = html.replace("{{" + a_p + "_SEARCH_QUERY}}", urllib.parse.quote(article["original_title"]))
    return html

def build_html(data):
    try:
        with open("template.html", "r", encoding="utf-8") as f: html_content = f.read()
    except FileNotFoundError:
        print("Error: template.html not found"); sys.exit(1)
    h = html_content
    h = h.replace("{{DATE_TODAY}}", data["date_today"])
    h = h.replace("{{TIME_NOW}}", data["time_now"])
    h = h.replace("{{SEC1_TITLE}}", "Mainstream Topics // 主流戰略議題")
    h = fill_section(h, data["mainstream_topics"], "MAIN", 5)
    h = h.replace("{{SEC2_TITLE}}", "Wildcard Topics // 潛在重大議題")
    h = fill_section(h, data["wildcard_topics"], "WILD", 3)
    h = h.replace("{{SEC3_TITLE}}", "Business & Finance // 全球商業與金融趨勢")
    h = fill_finance(h, data["business_finance_taiwan"], "FIN_TW")
    h = fill_finance(h, data["business_finance_global"], "FIN_GL")
    out = "daily_dashboard_rendered.html"
    with open(out, "w", encoding="utf-8") as f: f.write(h)
    print(f"Success: Generated {out}")

def main():
    for fn in ["enriched_intelligence.json", "raw_intelligence.json"]:
        try:
            with open(fn, "r", encoding="utf-8") as f:
                data = json.load(f); print(f"Rendering {fn}..."); build_html(data); return
        except FileNotFoundError: continue
    print("Error: No data files found.")

if __name__ == "__main__":
    main()
