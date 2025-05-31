from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List
from backend.app.db.session import get_db
from backend.app.db.models import Thread, Message
from backend.app.core.logging import logger
from sqlalchemy import select

router = APIRouter(prefix="/api/v1/threads", tags=["threads"])

@router.get("/", response_model=List[dict])
def list_threads(db = Depends(get_db)):
    threads = db.execute(Thread.__table__.select())
    result = threads.fetchall()
    logger.info("Listing threads", count=len(result))
    return [dict(row._mapping) for row in result]

@router.get("/{thread_id}", response_model=dict)
def thread_detail(thread_id: int, db = Depends(get_db)):
    thread = db.execute(Thread.__table__.select().where(Thread.id == thread_id))
    row = thread.fetchone()
    if not row:
        logger.warning("Thread not found", thread_id=thread_id)
        raise HTTPException(status_code=404, detail="Thread not found")
    return dict(row._mapping)

@router.post("/{thread_id}/pause")
def pause_thread(thread_id: int, db = Depends(get_db)):
    result = db.execute(Thread.__table__.select().where(Thread.id == thread_id))
    row = result.fetchone()
    if not row:
        logger.warning("Thread not found for pause", thread_id=thread_id)
        raise HTTPException(status_code=404, detail="Thread not found")
    db.execute(Thread.__table__.update().where(Thread.id == thread_id).values(status="paused"))
    db.commit()
    logger.info("Thread paused", thread_id=thread_id)
    return {"ok": True, "status": "paused"}

@router.post("/{thread_id}/resume")
def resume_thread(thread_id: int, db = Depends(get_db)):
    result = db.execute(Thread.__table__.select().where(Thread.id == thread_id))
    row = result.fetchone()
    if not row:
        logger.warning("Thread not found for resume", thread_id=thread_id)
        raise HTTPException(status_code=404, detail="Thread not found")
    db.execute(Thread.__table__.update().where(Thread.id == thread_id).values(status="active"))
    db.commit()
    logger.info("Thread resumed", thread_id=thread_id)
    return {"ok": True, "status": "active"}

@router.get("/{thread_id}/messages", response_model=List[dict])
def get_thread_messages(thread_id: int, db = Depends(get_db)):
    messages = db.execute(
        select(Message).where(Message.thread_id == thread_id).order_by(Message.created_at.asc())
    ).scalars().all()
    return [
        {
            "id": m.id,
            "content": m.content,
            "role": m.role,
            "model": m.model,
            "created_at": m.created_at,
            "tool_call_id": None  # Extend if tool calls are tracked
        }
        for m in messages
    ]

@router.post("/{thread_id}/messages", response_model=List[dict])
def post_thread_message(thread_id: int, db = Depends(get_db), body: dict = Body(...)):
    content = body.get("content")
    if not content:
        raise HTTPException(status_code=400, detail="Content required")
    # Create new user message
    msg = Message(
        thread_id=thread_id,
        content=content,
        role="user",
        model=None
    )
    db.add(msg)
    db.commit()
    # Return updated list
    messages = db.execute(
        select(Message).where(Message.thread_id == thread_id).order_by(Message.created_at.asc())
    ).scalars().all()
    return [
        {
            "id": m.id,
            "content": m.content,
            "role": m.role,
            "model": m.model,
            "created_at": m.created_at,
            "tool_call_id": None
        }
        for m in messages
    ] 