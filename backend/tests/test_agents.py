import pytest
from backend.app.db.models import Thread
from backend.app.db.session import get_db
from backend.app.agents.data_agent import run_data_agent
import os
import time
from slack_sdk import WebClient

def create_thread(status="active", agent="data_agent"):
    db = next(get_db())
    thread = Thread(status=status, agent=agent)
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread.id

def get_thread_status(thread_id):
    db = next(get_db())
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    return thread.status if thread else None

def set_thread_status(thread_id, status):
    db = next(get_db())
    db.query(Thread).filter(Thread.id == thread_id).update({"status": status})
    db.commit()

@pytest.mark.asyncio
async def test_data_agent_start():
    thread_id = create_thread(status="planning")
    # Simulate agent start
    set_thread_status(thread_id, "active")
    assert get_thread_status(thread_id) == "active"

@pytest.mark.asyncio
async def test_data_agent_pause():
    thread_id = create_thread(status="active")
    set_thread_status(thread_id, "paused")
    assert get_thread_status(thread_id) == "paused"

@pytest.mark.asyncio
async def test_data_agent_complete():
    thread_id = create_thread(status="active")
    set_thread_status(thread_id, "success")
    assert get_thread_status(thread_id) == "success"

@pytest.mark.asyncio
async def test_data_agent_error():
    thread_id = create_thread(status="active")
    set_thread_status(thread_id, "failed")
    assert get_thread_status(thread_id) == "failed"

@pytest.mark.asyncio
async def test_run_data_agent_lifecycle():
    thread_id = create_thread(status="planning")
    result = await run_data_agent(thread_id)
    assert result["ok"] is True
    assert get_thread_status(thread_id) == "success"

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_TEST_CHANNEL = os.getenv("SLACK_TEST_CHANNEL")  # Add this to .env for test channel

pytestmark = pytest.mark.skipif(
    not (SLACK_BOT_TOKEN and SLACK_APP_TOKEN and SLACK_TEST_CHANNEL),
    reason="Slack tokens or test channel not set in .env"
) 