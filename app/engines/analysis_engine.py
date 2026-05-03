def normalize_event(event_type: str, title: str, summary: str, timestamp: str, related_stocks: list[str], sector: str):
    return {
        "event_type": event_type,
        "title": title,
        "summary": summary,
        "timestamp": timestamp,
        "related_stocks": related_stocks,
        "sector": sector,
    }

def should_trigger_alert(analysis: dict) -> bool:
    return bool(
        analysis.get("is_relevant")
        and analysis.get("confidence_score", 0) >= 70
        and analysis.get("impact_strength") in {"medium", "high"}
    )
