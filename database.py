import sqlite3
import json
from datetime import datetime

DB_NAME = "intelligence.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 建立主題表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        section_key TEXT,
        topic_title TEXT,
        risk_badge TEXT,
        badge_text TEXT,
        risk_reason TEXT,
        topic_summary TEXT,
        global_search_url TEXT
    )
    ''')
    
    # 建立文章表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER,
        source_tag TEXT,
        front_title TEXT,
        back_title TEXT,
        back_summary TEXT,
        original_title TEXT,
        source_url TEXT,
        image_url TEXT,
        FOREIGN KEY (topic_id) REFERENCES topics (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def save_dashboard_data(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    date_today = data.get("date_today", datetime.now().strftime("%Y-%m-%d"))
    
    sections = [
        ('mainstream_topics', data.get('mainstream_topics')),
        ('wildcard_topics', data.get('wildcard_topics')),
        ('business_finance_taiwan', data.get('business_finance_taiwan')),
        ('business_finance_global', data.get('business_finance_global'))
    ]
    
    for sec_key, section in sections:
        if not section: continue
        for topic in section.get('topics', []):
            cursor.execute('''
            INSERT INTO topics (date, section_key, topic_title, risk_badge, badge_text, risk_reason, topic_summary, global_search_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                date_today,
                sec_key,
                topic.get('topic_title'),
                topic.get('risk_badge'),
                topic.get('badge_text'),
                topic.get('risk_reason'),
                topic.get('topic_summary'),
                topic.get('global_search_url')
            ))
            topic_id = cursor.lastrowid
            
            for article in topic.get('articles', []):
                cursor.execute('''
                INSERT INTO articles (topic_id, source_tag, front_title, back_title, back_summary, original_title, source_url, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    topic_id,
                    article.get('source_tag'),
                    article.get('front_title'),
                    article.get('back_title'),
                    article.get('back_summary'),
                    article.get('original_title'),
                    article.get('source_url'),
                    article.get('image_url')
                ))
    
    conn.commit()
    conn.close()
    print(f"✅ 資料已成功存入資料庫: {DB_NAME}")

if __name__ == "__main__":
    init_db()
