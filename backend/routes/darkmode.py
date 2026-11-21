from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import DarkmodeState, DarkmodeStateRequest


router = APIRouter()


@router.post("/api/v1/darkmode/state")
async def save_darkmode_state(data: DarkmodeStateRequest, db: Session = Depends(get_db)):
    item = db.query(DarkmodeState).filter(DarkmodeState.origin == data.origin).first()
    if item is None:
        item = DarkmodeState(
            origin=data.origin,
            enabled=data.enabled,
            last_updated=datetime.now(timezone.utc),
        )
        db.add(item)
    else:
        item.enabled = data.enabled
        item.last_updated = datetime.now(timezone.utc)

    db.commit()

    return {
        "status": "saved",
        "data": {
            "origin": data.origin,
            "enabled": data.enabled,
        },
    }


@router.get("/api/v1/darkmode/state/{origin:path}")
async def get_darkmode_state(origin: str, db: Session = Depends(get_db)):
    item = db.query(DarkmodeState).filter(DarkmodeState.origin == origin).first()
    if item is None:
        return {
            "origin": origin,
            "enabled": False,
            "last_updated": None,
        }

    return {
        "origin": origin,
        "enabled": bool(item.enabled),
        "last_updated": item.last_updated.isoformat() if item.last_updated else None,
    }

