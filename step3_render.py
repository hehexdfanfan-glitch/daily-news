import json
import os
import sys
from jinja2 import Template, Environment, FileSystemLoader

def build_html(data):
    try:
        # 使用 Jinja2 載入新模板
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('template.html')
        
        # 準備渲染數據
        rendered_html = template.render(
            date_today=data.get("date_today"),
            time_now=data.get("time_now"),
            generated_by=data.get("generated_by", "Legacy Engine"),
            mainstream_topics=data.get("mainstream_topics"),
            wildcard_topics=data.get("wildcard_topics"),
            business_finance_taiwan=data.get("business_finance_taiwan"),
            business_finance_global=data.get("business_finance_global")
        )
        
        out = "daily_dashboard_rendered.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(rendered_html)
        print(f"✅ Success: Generated {out} (v2 with Jinja2)")
        
    except Exception as e:
        print(f"❌ Error during rendering: {e}")
        sys.exit(1)

def main():
    # 優先讀取 enriched 資料
    for fn in ["enriched_intelligence.json", "raw_intelligence.json"]:
        if os.path.exists(fn):
            try:
                with open(fn, "r", encoding="utf-8") as f:
                    data = json.load(f)
                print(f"🚀 Rendering {fn} using Phase 2 Engine...")
                build_html(data)
                return
            except Exception as e:
                print(f"⚠️ Failed to read {fn}: {e}")
                continue
    
    print("❌ Error: No valid data files found for rendering.")

if __name__ == "__main__":
    main()
