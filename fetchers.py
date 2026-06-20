"""
News fetchers for AI daily digest.
Each fetcher returns a list of dicts: {title, url, source, summary, lang}
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import feedparser
import requests
from bs4 import BeautifulSoup

from config import MAX_ITEMS_PER_SOURCE

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AINewsBot/1.0; +https://github.com/ai-news-daily)"
}


# ─── Hacker News (Algolia API) ───────────────────────────────────────────────

def fetch_hackernews(n: int = MAX_ITEMS_PER_SOURCE) -> list[dict]:
    """Fetch top AI-related stories from Hacker News via Algolia search."""
    ai_keywords = ["AI", "LLM", "GPT", "Claude", "OpenAI", "machine learning",
                   "deep learning", "NLP", "transformer", "diffusion", "neural",
                   "AGI", "RLHF", "fine-tune", "RAG", "vector", "embedding",
                   "agent", "prompt", "inference", "GPU"]
    query = " OR ".join(ai_keywords)
    url = "https://hn.algolia.com/api/v1/search_by_date"
    try:
        r = requests.get(url, params={
            "query": query,
            "tags": "story",
            "hitsPerPage": n,
            "numericFilters": "points>20"
        }, headers=HEADERS, timeout=15)
        r.raise_for_status()
        hits = r.json().get("hits", [])
        results = []
        for h in hits:
            results.append({
                "title": h.get("title", "").strip(),
                "url": h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
                "source": "Hacker News",
                "summary": f"👍 {h.get('points', 0)} pts | 💬 {h.get('num_comments', 0)} comments",
                "lang": "en",
            })
        log.info(f"HackerNews: fetched {len(results)} stories")
        return results
    except Exception as e:
        log.warning(f"HackerNews fetch failed: {e}")
        return []


# ─── ArXiv (cs.AI) ────────────────────────────────────────────────────────────

def fetch_arxiv(n: int = MAX_ITEMS_PER_SOURCE) -> list[dict]:
    """Fetch latest AI papers from ArXiv (cs.AI + cs.CL)."""
    url = "http://export.arxiv.org/api/query"
    # Get papers from last 2 days, sorted by submission date
    params = {
        "search_query": "cat:cs.AI OR cat:cs.CL",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": n * 2,  # Fetch extra to filter
        "start": 0,
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=20)
        r.raise_for_status()
        feed = feedparser.parse(r.text)
        results = []
        for entry in feed.entries[:n]:
            # Use arxiv ID as fallback URL
            arxiv_id = entry.id.split("/abs/")[-1] if "/abs/" in entry.id else ""
            results.append({
                "title": entry.title.strip().replace("\n", " "),
                "url": entry.link or f"https://arxiv.org/abs/{arxiv_id}",
                "source": "ArXiv",
                "summary": entry.summary.strip()[:200].replace("\n", " ") if hasattr(entry, "summary") else "",
                "lang": "en",
            })
        log.info(f"ArXiv: fetched {len(results)} papers")
        return results
    except Exception as e:
        log.warning(f"ArXiv fetch failed: {e}")
        return []


# ─── 机器之心 (jiqizhixin.com) ───────────────────────────────────────────────

def fetch_jiqizhixin(n: int = MAX_ITEMS_PER_SOURCE) -> list[dict]:
    """Fetch AI news from 机器之心 (jiqizhixin.com)."""
    try:
        r = requests.get("https://www.jiqizhixin.com/api/articles",
                         params={"page": 1, "per_page": n},
                         headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        articles = data.get("data", []) if isinstance(data, dict) else data[:n]
        results = []
        for a in articles:
            results.append({
                "title": a.get("title", "").strip(),
                "url": f"https://www.jiqizhixin.com/articles/{a.get('id', '')}",
                "source": "机器之心",
                "summary": a.get("excerpt", "").strip()[:200] if a.get("excerpt") else "",
                "lang": "zh",
            })
        log.info(f"机器之心: fetched {len(results)} articles")
        return results
    except Exception as e:
        log.warning(f"机器之心 fetch failed: {e}")
        return []


# ─── 量子位 (qbitai.com) ─────────────────────────────────────────────────────

def fetch_qbitai(n: int = MAX_ITEMS_PER_SOURCE) -> list[dict]:
    """Fetch AI news from 量子位 (qbitai.com) via scraping."""
    try:
        r = requests.get("https://www.qbitai.com/", headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        results = []
        # Find article cards
        articles = soup.select("div.article-list div.article-item, article, div.card")
        if not articles:
            # Try alternate selector
            articles = soup.select("a[href*='/article/']")
            seen = set()
            for a in articles[:n]:
                title = a.get_text(strip=True)
                href = a.get("href", "")
                if not title or not href or title in seen:
                    continue
                seen.add(title)
                if not href.startswith("http"):
                    href = f"https://www.qbitai.com{href}"
                results.append({
                    "title": title,
                    "url": href,
                    "source": "量子位",
                    "summary": "",
                    "lang": "zh",
                })
        else:
            for item in articles[:n]:
                title_el = item.select_one("h2, h3, .title, a")
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                link_el = item.select_one("a[href]")
                href = link_el.get("href", "") if link_el else ""
                if href and not href.startswith("http"):
                    href = f"https://www.qbitai.com{href}"
                results.append({
                    "title": title,
                    "url": href or "https://www.qbitai.com/",
                    "source": "量子位",
                    "summary": "",
                    "lang": "zh",
                })
        log.info(f"量子位: fetched {len(results)} articles")
        return results
    except Exception as e:
        log.warning(f"量子位 fetch failed: {e}")
        return []


# ─── 36氪 (36kr.com) ─────────────────────────────────────────────────────────

def fetch_36kr(n: int = MAX_ITEMS_PER_SOURCE) -> list[dict]:
    """Fetch AI news from 36氪 via API."""
    try:
        r = requests.get(
            "https://www.36kr.com/api/search/article",
            params={"keyword": "AI 人工智能", "per_page": n},
            headers=HEADERS, timeout=15
        )
        r.raise_for_status()
        data = r.json()
        items = data.get("data", {}).get("items", [])
        results = []
        for item in items[:n]:
            results.append({
                "title": item.get("title", "").strip(),
                "url": f"https://www.36kr.com/p/{item.get('id', '')}",
                "source": "36氪",
                "summary": item.get("summary", "").strip()[:200] if item.get("summary") else "",
                "lang": "zh",
            })
        log.info(f"36氪: fetched {len(results)} articles")
        return results
    except Exception as e:
        log.warning(f"36氪 fetch failed: {e}")
        return []


# ─── Master fetcher ──────────────────────────────────────────────────────────

def fetch_all() -> list[dict]:
    """Fetch from all sources, merge, deduplicate."""
    all_news = []

    fetchers = [
        ("en", fetch_hackernews),
        ("en", fetch_arxiv),
        ("zh", fetch_jiqizhixin),
        ("zh", fetch_qbitai),
        ("zh", fetch_36kr),
    ]

    for lang, fetcher in fetchers:
        try:
            news = fetcher()
            all_news.extend(news)
        except Exception as e:
            log.error(f"Fetcher {fetcher.__name__} crashed: {e}")
            continue

    # Deduplicate by title similarity (simple: exact match)
    seen_titles = set()
    deduped = []
    for item in all_news:
        key = item["title"].lower().strip()[:80]
        if key not in seen_titles:
            seen_titles.add(key)
            deduped.append(item)

    log.info(f"Total after dedup: {len(deduped)} news items")
    return deduped
