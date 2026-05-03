import yfinance as yf
import feedparser
from datetime import datetime


def fetch_prices(symbol: str, period: str = "3mo"):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period=period)
    return data.reset_index().to_dict(orient="records")


def fetch_rss(feeds: list[str]):
    items = []
    for f in feeds:
        parsed = feedparser.parse(f)
        for e in parsed.entries:
            items.append({
                "title": e.get("title"),
                "summary": e.get("summary", ""),
                "url": e.get("link"),
                "published_at": e.get("published", str(datetime.utcnow())),
                "source": f,
            })
    return items
