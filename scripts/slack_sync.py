import os
from slack_sdk import WebClient
from backend.app.tools.raw_notes_tools import write_raw_notes
import time

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_TEST_CHANNEL = os.getenv("SLACK_TEST_CHANNEL")

client = WebClient(token=SLACK_BOT_TOKEN)

def sync_slack_messages():
    # Fetch last 100 messages from the test channel
    response = client.conversations_history(channel=SLACK_TEST_CHANNEL, limit=100)
    messages = response.get("messages", [])
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
            result = write_raw_notes.__wrapped__(data) if hasattr(write_raw_notes, "__wrapped__") else write_raw_notes(data)
            print(f"Synced: {data['content']} -> {result}")
        except Exception as e:
            print(f"Error syncing message: {e}")

if __name__ == "__main__":
    sync_slack_messages() 