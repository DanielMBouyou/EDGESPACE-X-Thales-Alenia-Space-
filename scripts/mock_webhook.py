from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="EDGE SPACE Mock Webhook")
EVENTS: List[Dict[str, Any]] = []


@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    payload["received_at"] = datetime.now(timezone.utc).isoformat()
    EVENTS.append(payload)
    return JSONResponse({"status": "ticket created", "event_id": payload.get("event_id")})


@app.get("/events")
async def events():
    return {"count": len(EVENTS), "events": EVENTS[-50:]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
