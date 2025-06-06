import hashlib
from datetime import datetime
from backend.app.db.models import RawNote, Message
from backend.app.db.session import get_db
from backend.app.core.logging import logger

async def read_raw_notes(filters=None):
    """
    Read raw notes with optional filtering.
    Args: filters: dict
    Returns: {"ok": True, "data": [notes]} or {"ok": False, "error": ...}
    """
    try:
        filters = filters or {}
        db = next(get_db())
        query = db.query(RawNote)
        if filters.get("source"):
            query = query.filter(RawNote.source == filters["source"])
        if filters.get("author"):
            query = query.filter(RawNote.author == filters["author"])
        if filters.get("after_date"):
            query = query.filter(RawNote.received_at >= datetime.fromisoformat(filters["after_date"]))
        if filters.get("before_date"):
            query = query.filter(RawNote.received_at <= datetime.fromisoformat(filters["before_date"]))
        if filters.get("content_query"):
            query = query.filter(RawNote.content.ilike(f"%{filters['content_query']}%"))
        notes = query.order_by(RawNote.received_at.desc()).limit(50).all()
        notes_data = [note.__dict__ for note in notes]
        logger.info("Raw notes retrieved", count=len(notes_data), filters=filters)
        return {"ok": True, "data": notes_data}
    except Exception as e:
        logger.error("Error reading raw notes", error=str(e), filters=filters)
        return {"ok": False, "error": str(e)}

async def write_raw_notes(data):
    """
    Write a new raw note, deduplicating by content_hash.
    Args: data: dict
    Returns: {"ok": True, "id": id} or {"ok": False, "error": ...}
    """
    try:
        db = next(get_db())
        content = data["content"]
        content_hash = hashlib.md5(content.encode()).hexdigest()
        existing = db.query(RawNote).filter(RawNote.content_hash == content_hash).first()
        if existing:
            return {"ok": True, "id": existing.id}
        note = RawNote(
            source=data["source"],
            source_note_id=data["source_note_id"],
            content=content,
            content_hash=content_hash,
            author=data.get("author"),
            channel=data.get("channel"),
            received_at=datetime.utcnow()
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        logger.info("Raw note written", id=note.id)
        return {"ok": True, "id": note.id}
    except Exception as e:
        logger.error("Error writing raw note", error=str(e), data=data)
        return {"ok": False, "error": str(e)}

async def write_message(data):
    """
    Write a new message to the messages table.
    Args: data: dict (must include thread_id, role, content; optional: model, tool_call_id)
    Returns: {"ok": True, "id": id} or {"ok": False, "error": ...}
    """
    try:
        db = next(get_db())
        msg = Message(
            thread_id=data["thread_id"],
            content=data["content"],
            role=data["role"],
            model=data.get("model"),
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        logger.info("Message written", id=msg.id, thread_id=msg.thread_id, role=msg.role)
        return {"ok": True, "id": msg.id}
    except Exception as e:
        logger.error("Error writing message", error=str(e), data=data)
        return {"ok": False, "error": str(e)}

async def read_messages(filters=None):
    """
    Read messages for a thread.
    Args: filters: dict (must include thread_id)
    Returns: {"ok": True, "data": [messages]} or {"ok": False, "error": ...}
    """
    try:
        db = next(get_db())
        thread_id = filters["thread_id"]
        query = db.query(Message).filter(Message.thread_id == thread_id).order_by(Message.created_at.asc())
        messages = query.all()
        messages_data = [
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
        logger.info("Messages retrieved", count=len(messages_data), thread_id=thread_id)
        return {"ok": True, "data": messages_data}
    except Exception as e:
        logger.error("Error reading messages", error=str(e), filters=filters)
        return {"ok": False, "error": str(e)} 