"""
AI Daily News — Main entry point.
Fetches AI news from multiple sources, summarizes with Claude, sends via email.
"""
import logging
import sys
from datetime import datetime, timezone, timedelta

from fetchers import fetch_all
from summarizer import summarize_news
from email_sender import send_email

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("ai-news-daily")

BJ_TZ = timezone(timedelta(hours=8))


def main():
    now = datetime.now(BJ_TZ)
    log.info(f"=== AI Daily News — {now.strftime('%Y-%m-%d %H:%M')} 北京时间 ===")

    # Step 1: Fetch
    log.info("Step 1/3: Fetching news from all sources...")
    news = fetch_all()
    if not news:
        log.error("No news fetched from any source. Check network or source availability.")
        # Still send a notice email
        html = """<p style="color:#dc2626;">今日未能获取到新闻数据，请检查网络或API配置。</p>"""
    else:
        log.info(f"Fetched {len(news)} news items total")

        # Step 2: Summarize
        log.info("Step 2/3: Summarizing with Claude...")
        html = summarize_news(news)

    # Step 3: Send email
    log.info("Step 3/3: Sending email...")
    success = send_email(html)

    if success:
        log.info("Done! Email sent successfully. ✅")
    else:
        log.error("Email sending failed. ❌")
        sys.exit(1)


if __name__ == "__main__":
    main()
