import os
import time
import pytest
from slack_sdk import WebClient

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_TEST_CHANNEL = os.getenv("SLACK_TEST_CHANNEL")  # Add this to .env for test channel

pytestmark = pytest.mark.skipif(
    not (SLACK_BOT_TOKEN and SLACK_APP_TOKEN and SLACK_TEST_CHANNEL),
    reason="Slack tokens or test channel not set in .env"
)

def test_slack_channel_message_visible():
    """
    Sends a message to the test channel and checks if it appears in the channel history.
    """
    client = WebClient(token=SLACK_BOT_TOKEN)
    # Send a message
    test_text = "integration test message"
    response = client.chat_postMessage(channel=SLACK_TEST_CHANNEL, text=test_text)
    assert response["ok"]
    ts = response["ts"]
    time.sleep(2)
    # Fetch channel history
    history = client.conversations_history(channel=SLACK_TEST_CHANNEL, limit=10)
    messages = history["messages"]
    # Check if our message is present
    found = any(m["ts"] == ts and m["text"] == test_text for m in messages)
    assert found, "Test message not found in channel history" 