import httpx
from app.core.config import settings

PROMPT_TEMPLATE = """You are a financial intelligence system specialized in BIST stocks.

Analyze the following event and determine its potential impact on the given stock.

Stock: {stock}
Sector: {sector}
Event: {event}
Macro Context: {macro}
Historical Patterns: {patterns}

Return structured JSON only."""

async def analyze_event(stock: str, sector: str, event: str, macro: str, patterns: str) -> str:
    prompt = PROMPT_TEMPLATE.format(stock=stock, sector=sector, event=event, macro=macro, patterns=patterns)
    payload = {"model": settings.ollama_model, "prompt": prompt, "stream": False}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(settings.ollama_url, json=payload)
        r.raise_for_status()
        return r.json().get("response", "{}")
