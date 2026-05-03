import httpx
from app.core.config import settings

async def send_telegram(message: str) -> dict:
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(url, json={"chat_id": settings.telegram_chat_id, "text": message})
        return {"ok": r.status_code == 200, "response": r.text}
