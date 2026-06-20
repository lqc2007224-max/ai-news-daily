"""
Summarize AI news using DeepSeek API and produce a beautiful HTML email.
"""
import logging
from datetime import datetime, timezone, timedelta

from openai import OpenAI

from config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL, MAX_TOTAL_NEWS

log = logging.getLogger(__name__)

BJ_TZ = timezone(timedelta(hours=8))

SYSTEM_PROMPT = """You are an AI news editor creating a daily digest for Chinese readers.
Your task: given a list of AI news headlines (mix of English and Chinese sources),
produce a concise, insightful summary in HTML format.

Rules:
1. Group news into 3-5 thematic clusters (e.g., "大模型新进展", "开源/AI工具", "行业/公司动态", "论文/研究前沿")
2. For each cluster, write 2-4 sentences of contextual analysis in Chinese — tell the reader WHY these matter
3. List the key headlines under each cluster with bilingual titles (keep English titles + brief Chinese annotation)
4. Highlight the 3 most important stories of the day at the top with a special marker
5. Use ONLY the news provided — don't invent anything
6. End with a "今日精选" section with 1-sentence takeaway for each top story
7. Keep the total output concise — aim for 600-1000 Chinese characters of original analysis

Return PURE HTML for the email body (the content area only, no <html>/<body> tags).
Style it beautifully: use a clean modern style with inline CSS, gradient header, card-like sections,
good typography, and accent colors (#1a56db blue family)."""


def summarize_news(news_items: list[dict]) -> str:
    """Send news to DeepSeek and get back an HTML summary."""
    if not news_items:
        return _fallback_html()

    # Limit total items (control cost)
    items = news_items[:MAX_TOTAL_NEWS]

    # Build the prompt
    news_text_parts = []
    for i, item in enumerate(items, 1):
        lang_tag = "🇬🇧" if item["lang"] == "en" else "🇨🇳"
        source_extra = f" | {item['summary']}" if item.get("summary") else ""
        news_text_parts.append(
            f"{i}. [{lang_tag} {item['source']}] {item['title']}{source_extra}\n   🔗 {item['url']}"
        )
    news_block = "\n\n".join(news_text_parts)

    user_message = f"""今天的AI新闻（{len(items)}条），请生成HTML摘要：

{news_block}"""

    try:
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com",
        )
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            max_tokens=4096,
            temperature=0.7,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        html_body = response.choices[0].message.content
        log.info(f"DeepSeek summary generated: {len(html_body)} chars")
        return html_body
    except Exception as e:
        log.error(f"DeepSeek API call failed: {e}")
        return _fallback_html()


def _fallback_html() -> str:
    """Fallback HTML when summarization fails."""
    now = datetime.now(BJ_TZ).strftime("%Y-%m-%d %H:%M")
    return f"""
    <div style="text-align:center;padding:40px;">
        <h2>⚠️ 今日摘要生成失败</h2>
        <p>生成时间: {now} (北京时间)</p>
        <p>请稍后查看或联系管理员检查 API 配置。</p>
    </div>
    """
