"""
Summarize AI news using DeepSeek API and produce a beautiful HTML email.
"""
import logging
import time
from datetime import datetime, timezone, timedelta

import httpx
from openai import OpenAI, APIConnectionError

from config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL, MAX_TOTAL_NEWS

log = logging.getLogger(__name__)

BJ_TZ = timezone(timedelta(hours=8))

# Custom HTTP client with longer timeouts
_http_client = httpx.Client(
    timeout=httpx.Timeout(connect=30.0, read=120.0, write=30.0, pool=30.0),
    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
)

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

    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
        http_client=_http_client,
        max_retries=0,
    )

    last_error = None
    for attempt in range(4):
        try:
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
            log.info(f"DeepSeek summary generated: {len(html_body)} chars (attempt {attempt + 1})")
            return html_body
        except (httpx.ConnectError, httpx.RemoteProtocolError, httpx.ReadTimeout, APIConnectionError) as e:
            last_error = e
            wait = 2 ** attempt
            log.warning(f"DeepSeek connection error (attempt {attempt + 1}/4), retrying in {wait}s: {e}")
            time.sleep(wait)
        except Exception as e:
            last_error = e
            log.error(f"DeepSeek API error (attempt {attempt + 1}/4): {e}")
            if attempt < 3:
                time.sleep(2 ** attempt)

    log.error(f"DeepSeek failed after 4 attempts: {last_error}")
    return _fallback_html(items)


def _fallback_html(news_items: list[dict] | None = None) -> str:
    """Build a simple HTML list of headlines when AI summarization fails."""
    now = datetime.now(BJ_TZ).strftime("%Y-%m-%d %H:%M")
    if not news_items:
        return f"""
        <div style="text-align:center;padding:40px;">
            <h2>⚠️ 今日摘要生成失败</h2>
            <p>生成时间: {now} (北京时间)</p>
            <p>请稍后查看或联系管理员检查 API 配置。</p>
        </div>
        """

    cards = []
    for i, item in enumerate(news_items[:25], 1):
        lang_icon = "🇬🇧" if item.get("lang") == "en" else "🇨🇳"
        source = item.get("source", "")
        title = item.get("title", "")
        url = item.get("url", "")
        extra = f" — {item['summary']}" if item.get("summary") else ""
        cards.append(f"""<div style="padding:12px 0;border-bottom:1px solid #e2e8f0;">
            <span style="color:#1a56db;font-weight:600;">{i}.</span>
            {lang_icon} <strong>[{source}]</strong>
            <a href="{url}" style="color:#1a1a2e;text-decoration:none;">{title}</a>
            <span style="color:#888;font-size:0.85em;">{extra}</span>
        </div>""")

    return f"""<div style="padding:10px 0;">
        <div style="background:#fef3c7;border-left:4px solid #f59e0b;padding:12px 16px;margin-bottom:20px;border-radius:0 8px 8px 0;">
            <strong>⚠️ AI 摘要暂时不可用</strong><br>
            <span style="font-size:0.9em;color:#92400e;">DeepSeek API 连接失败，以下是今日原始新闻列表。AI 摘要将在下次运行时自动恢复。</span>
        </div>
        <div style="font-size:0.85em;color:#888;margin-bottom:16px;">📋 共 {len(news_items)} 条新闻 · {now} (北京时间)</div>
        {"".join(cards)}
    </div>"""
