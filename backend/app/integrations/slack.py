import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from backend.app.core.logging import logger
from backend.app.tools.raw_notes_tools import write_raw_notes

def get_env_var(name):
    value = os.getenv(name)
    if not value:
        logger.error(f"Missing required environment variable: {name}")
    return value

app = App(token=get_env_var("SLACK_BOT_TOKEN"))

@app.message("hello")
def handle_hello(message, say):
    user = message['user']
    logger.info(f"Received hello from {user}")
    say(f"Hi there, <@{user}>!")
    logger.info(f"Sent reply to {user}")

@app.event("message")
def handle_message_events(body, event, logger):
    # Only process user messages (not bot messages, etc.)
    if event.get("subtype") is not None:
        return
    content = event.get("text", "")
    author = event.get("user", "")
    channel = event.get("channel", "")
    ts = event.get("ts", "")
    data = {
        "source": "slack",
        "source_note_id": ts,
        "content": content,
        "author": author,
        "channel": channel
    }
    try:
        result = write_raw_notes.__wrapped__(data) if hasattr(write_raw_notes, "__wrapped__") else write_raw_notes(data)
        logger.info(f"Wrote Slack message to raw_notes", result=result, data=data)
    except Exception as e:
        logger.error(f"Failed to write Slack message to raw_notes: {e}", data=data)

def start_slack_listener():
    handler = SocketModeHandler(app, get_env_var("SLACK_APP_TOKEN"))
    logger.info("Starting Slack SocketModeHandler")
    handler.start() 