from backend.app.db.session import SessionLocal
from sqlalchemy import text

def test_db_connection():
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1
    finally:
        session.close() 