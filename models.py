from pydantic import BaseModel, Field

class Article(BaseModel):
    article_id: str = Field(description="文章的唯一ID")
    source_tag: str = Field(description="來源媒體標籤")
    front_title: str = Field(description="卡片正面標題 (繁中)")
    back_title: str = Field(description="卡片背面標題 (繁中)")
    back_summary: str = Field(description="文章深度摘要 (繁中)")
    original_title: str = Field(description="原始網頁標題原文")
    source_url: str = Field(description="文章原始 URL")
    image_url: str = Field(default="", description="縮圖 URL")

class Topic(BaseModel):
    topic_id: str = Field(description="主題 ID")
    risk_badge: str = Field(description="CSS class")
    badge_text: str = Field(description="標籤文字 (繁中)")
    topic_title: str = Field(description="主題大標題 (繁中)")
    risk_reason: str = Field(description="重要性解釋 (繁中)")
    topic_summary: str = Field(description="該主題總結 (繁中)")
    global_search_url: str = Field(description="Google News 搜尋網址")
    articles: list[Article] = Field(description="文章列表")

class Section(BaseModel):
    section_title: str = Field(description="區段標題")
    topics: list[Topic] = Field(description="主題列表")

class DashboardData(BaseModel):
    date_today: str = Field(description="YYYY-MM-DD")
    time_now: str = Field(description="HH:MM:SS CST")
    mainstream_topics: Section
    wildcard_topics: Section
    business_finance_taiwan: Section
    business_finance_global: Section
