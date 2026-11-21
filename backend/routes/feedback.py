from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import FeedbackEntry, FeedbackRequest, parse_event_time


router = APIRouter()


@router.post("/api/v1/feedback")
async def submit_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)):
    item = FeedbackEntry(
        feedback_type=feedback.feedback_type,
        comment=(feedback.comment or "").strip() or None,
        origin=feedback.origin,
        extension_version=feedback.extension_version,
        anonymous_user_id=feedback.anonymous_user_id,
        created_at=parse_event_time(feedback.timestamp),
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "status": "saved",
        "feedback_id": int(item.id),
    }


@router.get("/api/v1/feedback/stats")
async def get_feedback_stats(origin: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(FeedbackEntry)
    if origin:
        query = query.filter(FeedbackEntry.origin == origin)

    total = query.count()
    likes = query.filter(FeedbackEntry.feedback_type == "like").count()
    dislikes = query.filter(FeedbackEntry.feedback_type == "dislike").count()

    return {
        "total": total,
        "likes": likes,
        "dislikes": dislikes,
        "origin": origin,
    }

