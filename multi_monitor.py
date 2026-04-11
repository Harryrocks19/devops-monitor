import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from models import MonitorTarget


async def check_target(target: MonitorTarget) -> dict:
    """Ping a monitored endpoint and return its status."""
    start = datetime.now()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(target.url)
        latency = (datetime.now() - start).total_seconds() * 1000
        return {
            "id":          target.id,
            "name":        target.name,
            "url":         target.url,
            "status":      "up" if response.status_code < 400 else "degraded",
            "status_code": response.status_code,
            "latency_ms":  round(latency, 2),
            "checked_at":  datetime.now().isoformat(),
        }
    except Exception as e:
        latency = (datetime.now() - start).total_seconds() * 1000
        return {
            "id":          target.id,
            "name":        target.name,
            "url":         target.url,
            "status":      "down",
            "status_code": None,
            "latency_ms":  round(latency, 2),
            "error":       str(e),
            "checked_at":  datetime.now().isoformat(),
        }


async def check_all_targets(db: Session) -> dict:
    """Check all registered monitor targets."""
    targets = db.query(MonitorTarget).filter(MonitorTarget.active == True).all()

    if not targets:
        return {
            "status":  "no_targets",
            "message": "No active targets. Add targets via POST /monitor/targets",
            "results": []
        }

    results = []
    for target in targets:
        result = await check_target(target)
        results.append(result)

    up_count   = sum(1 for r in results if r["status"] == "up")
    down_count = sum(1 for r in results if r["status"] == "down")

    return {
        "timestamp":   datetime.now().isoformat(),
        "total":       len(results),
        "up":          up_count,
        "down":        down_count,
        "degraded":    len(results) - up_count - down_count,
        "results":     results,
    }
