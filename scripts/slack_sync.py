import os
import sys
from loguru import logger
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from slack_sdk import WebClient
from backend.app.tools.raw_notes_tools import write_raw_notes
import time

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_TEST_CHANNEL = os.getenv("SLACK_TEST_CHANNEL")

logger.remove()
logger.add("logs/slack_sync.log", rotation="00:00", retention="90 days", level="INFO", serialize=False)

client = WebClient(token=SLACK_BOT_TOKEN)

def sync_slack_messages():
    logger.info("Starting Slack sync", channel=SLACK_TEST_CHANNEL)
    response = client.conversations_history(channel=SLACK_TEST_CHANNEL, limit=100)
    messages = response.get("messages", [])
    async def process_messages():
        for msg in messages:
            if "subtype" in msg:
                continue  # skip non-user messages
            data = {
                "source": "slack",
                "source_note_id": msg["ts"],
                "content": msg.get("text", ""),
                "author": msg.get("user", ""),
                "channel": SLACK_TEST_CHANNEL
            }
            try:
                result = await write_raw_notes(data)
                logger.info("Synced Slack message", data=data, result=result)
            except Exception as e:
                logger.error("Error syncing Slack message", error=str(e), data=data)
    asyncio.run(process_messages())

if __name__ == "__main__":
    sync_slack_messages() 