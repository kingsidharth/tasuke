# Tasuke MVP Development Plan (v1.2 – 31 May 2025)

> **Purpose** – A local‑first automation stack that captures work‑stream data (Slack, Granola notes), organises it into tasks & projects, and surfaces just‑in‑time actions through specialised AI agents.

---

## 1. Functional Requirements

### 1.1 Core Workflows

* **Capture** – Ingest Slack mentions/channels and (Phase 5) Granola notes into `raw_notes`; agent conversation `messages` remain internal to threads.
* **Organise** – Transform qualifying messages into `tasks`; link to `projects`.
* **Plan & Review** – Generate daily agendas, detect stalled threads, surface next actions.
* **Interact** – Chat with any agent inside a thread; agents may pause awaiting confirmation.
* **Control** – Pause/resume threads, assign/complete tasks, tweak settings.
* **Archive** – Nightly pg‑dump & log rotation (90‑day retention).

### 1.2 User Interface Requirements

**Dashboard**

* Health: Total Threads — Completed, Ongoing, Error, Queued (Last 24 hrs)
* Live list of threads with status chips (`queued`, `active`, `paused`, …). *Paused threads* are visually highlighted for quick action.

  * Clicking on thead opens Chat Detail View of that thread
* Sidebar of agents → opens chat window or Chat Detail View (new chat)
* Inline controls: **pause / resume / post** to any thread.

**Thread/Chat Detail View**: Where we user can enter any ongoing/paused/conclude thread and see all the messages sequentially

1. Messages history + tool calls history — oldest first
2. UI Controls + Status 
3. **File Uploads**

   * Chat windows allow optional upload of images & PDFs; backend saves to `storage/uploads/` and passes file handle to OpenRouter as `file` param (see OpenRouter file API). \*\*
   * Paths & tokens (Slack, Granola DB, OpenRouter API key, etc.).

**Tasks View**

* Kanban (My Tasks, Team Tasks). Create/Edit, drag between columns.
* Embedded *Project Manager Agent* chat panel.

**Logs View**

* Scrollable log stream with filters (level, component, timeframe)
* Search + Filter

**Database View**

* Allow browsing actual tables in the DB (show last 100 entries + pagination)
* Search + filters 
* For relevant tables/rows — show status of embeddings (pending, creating, available)
* Allow UI Controls — Edit, Delete, Add New

  * For each of these changes show a confirmation dialogue

**Settings**

* Manual Data Sync Options
* S3 integration Settings
* Backup: Dropbox path, trigger pg dump

### 1.3 Logging Requirements

* Library: **loguru** (JSON sink + colour console)
  Docs → [https://github.com/Delgan/loguru](https://github.com/Delgan/loguru)
* **Log every**:

  * Agent lifecycle events (start, success, error, pause, resume).
  * Tool invocations & latency.
  * LLM call metadata (model, tokens, cost).
  * DB write failures & retries.
* **Storage**: `logs/` directory in repo root, rotated daily, delete >90 days via `loguru.logger.add(..., rotation="00:00", retention="90 days")`.

### 1.4 Agents & Responsibilities

#### Data Agent

* **Trigger:** Slack webhooks (app mentions, channel messages).
* **Tools:** `write_raw_notes`, `write_messages`, `write_tasks`, `write_projects`.
* **Flow:** Writes incoming Slack events to `raw_notes`; may open or append to an agent thread when follow‑up reasoning is required.
* **Completion:** Writes `system` message "COMPLETED" → sets thread `status = success` and `completed_at`.
* **Pauses:** Calls `ask_for_confirmation(prompt)` which auto‑pauses the thread until a human resumes via UI.

#### Project Manager Agent

* **Trigger:** Automatically when a new row appears in `raw_notes` **or** manual "Run PM" button.
* **Tools:** `read_raw_notes`, `read_tasks`, `update_task`, `update_project`, `ask_for_confirmation`.
* **Policy:** After each substantive change, calls `ask_for_confirmation` — pausing the thread.
* **Error Handling:** On exception increments `error_count`, sets `status = failed`, and calls `contact_human`.

#### Curator Agent

* **Trigger:** Daily at 00:00 (midnight).
* **Tools:** `read_threads`, `update_thread`, `contact_human`.
* Marks thread `success` on finish.

#### Planner Agent

* **Trigger:** Daily at 03:00.
* **Tools:** `read_tasks`, `update_task`, `contact_human`.
* Writes agenda summary then marks thread `success`.

##### Thread Lifecycle & Error Handling (LangGraph conventions)

* **Running → Paused:** `contact_human` or `ask_for_confirmation` triggers `graph.interrupt()`; sets `threads.status = paused`.
* **Paused → Resumed:** GUI **resume** button or posting a message sends `resume` command to LangGraph, restoring state.
* **Error:** Try/except routes to `ErrorNode`, increments `error_count`, stores `last_error`, sets `status = failed`; retry policy attempts 3×.
* **Completion:** Agent writes `system` message "COMPLETED"; wrapper sets `status = success`, `completed_at`.

## 1.5 Integration Requirements

* **Slack** – Socket Mode events; scopes: `app_mentions:read`, `channels:history`, `chat:write`. Personal mentions captured by filtering `<@YOUR_ID>`.
* **OpenRouter streaming** – Set `stream=true`, iterate SSE chunks to feed Reflex UI.
* **OpenRouter tool calling** – Set `tool_choice="auto"` and include JSON schema; consult [https://openrouter.ai/docs/features/tool-calling](https://openrouter.ai/docs/features/tool-calling) for response format.
* **Images / PDFs** – File uploads supported via multipart; forward `file` param to OpenRouter per [https://openrouter.ai/docs/features/images-and-pdfs](https://openrouter.ai/docs/features/images-and-pdfs).
* **Prompt caching** – Enable `cache=true` header to leverage shared cache ([https://openrouter.ai/docs/features/prompt-caching](https://openrouter.ai/docs/features/prompt-caching)).
* **Framework adapters** – LangGraph uses OpenAI‑compatible SDK; confirmed in [https://openrouter.ai/docs/community/frameworks](https://openrouter.ai/docs/community/frameworks).
* **Granola** – (Phase 5) SQLite export script; upsert into `raw_notes`.
* **Slack** – Socket Mode events; scopes: `app_mentions:read`, `channels:history`, `chat:write`. Personal mentions captured by filtering `<@USERID>`.
* **OpenRouter streaming** – Pass `stream=true` in `ChatCompletion.create`; iterate over SSE chunks to stream to Reflex chat UI.
  Example:

  ```python
  client = openai.ChatCompletion()
  for chunk in client.create(model=model, messages=msgs, stream=True):
      yield chunk.choices[0].delta.content
  ```

  Docs → [https://openrouter.ai/docs/api-reference/streaming](https://openrouter.ai/docs/api-reference/streaming)
* **Granola** – (Phase 5) SQLite export → periodic script; each note hash‑checked then upserted as `messages`.

---

## 2. Selected Tech Stack (with links)

* FastAPI – [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)
* LangGraph – [https://python.langgraph.org](https://python.langgraph.org)
* PostgreSQL 16 – [https://www.postgresql.org](https://www.postgresql.org)
* pgvector – [https://github.com/pgvector/pgvector](https://github.com/pgvector/pgvector)
* SQLAlchemy 2.0 – [https://docs.sqlalchemy.org](https://docs.sqlalchemy.org)
* Alembic – [https://alembic.sqlalchemy.org](https://alembic.sqlalchemy.org)
* Celery 5 – [https://docs.celeryq.dev](https://docs.celeryq.dev)
* Redis 7 – [https://redis.io](https://redis.io)
* Reflex – [https://reflex.dev](https://reflex.dev)
* shadcn/ui – [https://ui.shadcn.com](https://ui.shadcn.com)
* Node 20 LTS – [https://nodejs.org](https://nodejs.org)
* **uv** – [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)
* **loguru** – [https://github.com/Delgan/loguru](https://github.com/Delgan/loguru)
* OpenRouter SDK – [https://docs.openrouter.ai/reference/python](https://docs.openrouter.ai/reference/python)

  * [https://openrouter.ai/docs/community/frameworks](https://openrouter.ai/docs/community/frameworks)
* FastAPI – [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)
* LangGraph – [https://python.langgraph.org](https://python.langgraph.org)
* PostgreSQL 16 – [https://www.postgresql.org](https://www.postgresql.org)
* pgvector – [https://github.com/pgvector/pgvector](https://github.com/pgvector/pgvector)
* SQLAlchemy 2.0 – [https://docs.sqlalchemy.org](https://docs.sqlalchemy.org)
* Alembic – [https://alembic.sqlalchemy.org](https://alembic.sqlalchemy.org)
* Celery 5 – [https://docs.celeryq.dev](https://docs.celeryq.dev)
* Redis 7 – [https://redis.io](https://redis.io)
* Reflex – [https://reflex.dev](https://reflex.dev)
* shadcn/ui – [https://ui.shadcn.com](https://ui.shadcn.com)
* Node 20 LTS – [https://nodejs.org](https://nodejs.org)
* **uv** (pkg manager) – [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv) *(fallback: pip)*
* **loguru** – [https://github.com/Delgan/loguru](https://github.com/Delgan/loguru)
* Slack Bolt Python – [https://github.com/slackapi/bolt-python](https://github.com/slackapi/bolt-python)

---

## 3. Project Structure

```text
.venv/                 # root virtual env
requirements.txt
logs/                  # loguru JSON files (rotated daily)
storage/               # uploaded images, PDFs  (90‑day retention)
docs/
backend/
  tests/
  app/
    api/
    agents/
    db/
    tools/
  alembic/
  worker/
frontend/
  reflex_app/
scripts/
  fetch_granola.py
.env.example
README.md
tasks.md
CHANGELOG.md
```

## **4. Core Database Schema**

\*BIGINT identity PKs; \`created\_at\` / \`updated\_at\` default to \`now()\`, unless noted.\*

### raw\_notes

* \`id\`
* \`source\` TEXT ("slack", "granola")
* \`source\_note\_id\` TEXT UNIQUE NOT NULL
* \`content\` TEXT
* \`content\_hash\` TEXT GENERATED ALWAYS AS (md5(content)) STORED
* \`author\` TEXT
* \`channel\` TEXT NULL
* \`content\_vector\` VECTOR(768)
* \`received\_at\`

**Deduplication**: unique on \`content\_hash\` to ignore exact duplicates.

### threads

* \`id\`
* \`created\_at\` / \`updated\_at\`
* \`status\` TEXT (\`planning\`, \`active\`, \`on\_hold\`, \`completed\`, \`archived\`)
* \`completed\_at\` TIMESTAMPTZ NULL \*(set when status → success)\*
* \`error\_count\` INT DEFAULT 0
* \`last\_error\` TEXT NULL
* \`agent\` TEXT
* \`summary\` TEXT
* \`summary\_embedding\` VECTOR(1536)

### messages

* \`id\`
* \`thread\_id\` FK→threads.id (NOT NULL)
* \`content\` TEXT
* \`content\_vector\` VECTOR(768) \*(for semantic dedup / search)\*
* \`role\` TEXT
* \`model\` TEXT
* \`tokens\_used\` INT (Returned by OpenRouter)
* \`created\_at\`

**Deduplication** – unique constraint on \`(role, content\_hash)\` where \`content\_hash = md5(content)\`.

### tasks

* \`id\`
* \`description\` TEXT
* \`assignee\` TEXT NULL (String name, null means Sidharth)
* \`status\` TEXT (pending|archived|done)
* \`priority\` SMALLINT (1-3)
* \`project\_id\` FK→projects.id
* \`due\_date\` DATE NULL
* \`created\_by\` TEXT (agent name or "human")
* \`updated\_by\` TEXT (agent name or "human")
* \`created\_at\` / \`updated\_at\`

**Deduplication**: hash of \`description\`; ignore if same hash exists & status ≠ done.

### projects

* \`id\`
* \`name\` TEXT UNIQUE NOT NULL
* \`description\` TEXT
* \`status\` TEXT (\`active\`, \`on\_hold\`, \`completed\`, \`archived\`)
* \`created\_at\` TIMESTAMPTZ DEFAULT now()
* \`updated\_at\` TIMESTAMPTZ DEFAULT now()

## 5 Tool Contracts

### Conventions

All tools exchange JSON. On error they return `{ "ok": false, "error": "…" }`. The backend logs the error, increments `error_count`, and, unless the thread is already paused, sets `threads.status = failed`.

### raw\_notes

* **read\_raw\_notes(filters)**

  * *Filters* (all optional): `source`, `author`, `after_date`, `before_date`, `content_query`, `vector_query` (cosine ≥ 0.8).
  * Results ordered by `created_at DESC`.
* **write\_raw\_notes(data)**

  * *Required*: `source`, `source_note_id`, `content`.
  * *Optional*: `author`, `channel`.
  * Backend computes `content_hash = md5(content)`; if that hash already exists the request is deduplicated and existing note ID returned.

### messages

* **read\_messages(filters)** — `thread_id`, `role`, `after_id`, `before_id`; default `id ASC`.
* **write\_messages(data)** — `thread_id`, `content`, `role`; optional `model`, `tokens_used`.

  * When `role="system"` and `content="COMPLETED"`, service sets `threads.status = success` and `completed_at = now()`.

### tasks

* **read\_tasks(filters)** — `status`, `assignee`, `project_id`, `after_date`, `before_date`; default sort by `due_date ASC NULLS LAST`.
* **write\_tasks(data)** — `description` (required); optional `assignee`, `project_id`, `due_date`.

  * Backend sets `created_by` from calling agent name.
* **update\_task(id, changes)** — allow changes to `description`, `status`, `assignee`, `due_date`, `project_id`; service auto‑fills `updated_by` and `updated_at`.

### projects

* **read\_projects(filters)** — `name_contains`, `status`.
* **update\_project(id, changes)** — `description`, `status`.

### meta tools

* **contact\_human(prompt)** and **ask\_for\_confirmation(prompt)** both append a `system` message with the prompt, set `threads.status = paused`, and await a human `user` reply via UI. Any human reply automatically flips `status` back to the previous active state and processing continues.

## read\_raw\_notes(filters)

\- Filters: \`source\`, \`author\`, \`after\_date\`, \`before\_date\`, \`content\_query\`, \`vector\_query\` (cosine ≥ 0.8).

\- Default sort: \`created\_at DESC\`.

### write\_raw\_notes(data)

\- Required: \`source\`, \`source\_note\_id\`, \`content\`.

\- Optional: \`author\`, \`channel\`.

\- Auto‑compute \`content\_hash = md5(content)\`; ignore insert if hash exists (dedup).

### read\_messages(filters)

## 6. Shared Prompt Template Shared Prompt Template

```

# Objective

{objective}

# Context

{context}

# Instructions

{instructions}

# Output Requirements

{output}

# Examples

{examples}

+ Tool Definitions


```

Each agent must be defined in it's on .py file 

Use f'strings so variables can be inserted dynamically

## 7. MVP Execution Phases  (each ships a UI slice)

### Phase 0 – Bootstrap

* Repo skeleton, ``.venv`, `requirements.txt``, .env, etc. 
* Reflex splash page hitting \`/health\`.
* Create DB, tables, install pg\_vector, etc.
* Slack listener → messages table&#x20;

  * populate with last 30 days, give a button to trigger this (later to be moved to settings)
* Database view + controls + search
* Manual refresh button to fetch Slack data (last 24 hrs)

### Phase 1 – Data Agent + Dashboard V1

* Implement first agent — Data Agent
* Dashboard lists threads (Slack only) with pause/resume.
* Ability to chat with agent, view threads, etc.
* Implement logging using loguru
* Background tasks — basics

### Phase 2 – Project Manager + Tasks UI

* Manual ProjectMgrAgent trigger.
* Tasks + PM chat + Projects
* File Uploads in chat
* Embeddings in background

### Phase 3 – Curator & Planner + Logs UI

* Nightly Curator; daily Planner.
* Logs page (loguru JSON tailer)
* Kanban implementation for Tasks

###  Phase 4 – Archival & Settings

* Settings page 
* pg‑dump to Dropbox for db backup, allow setting path in Settings

  * Ability to manually trigger pg\_dump to dropbox
* Ability to manually trigger slack sync
* Remaining UI and control

### Phase 5 – Granola Integration & Dashboard Enhancement

* \`fetch\_granola.py\` + button + give this as tool to data agent
* Dashboard adds Granola source filter.
* S3 integration for file uploads — allow uploading files to S3, that cleans-it up from local folder (Expose required fields in settings)

## 8. Slack Integration Details

1\. Create Slack App › enable Socket Mode.

2\. Add scopes: \`app\_mentions\:read\`, \`channels\:history\`, \`chat\:write\`.

3\. Use Slack Bolt Python; start:

```
python

from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=os.environ["SLACK_BOT_TOKEN"])

handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])

handler.start()
```

Personal mentions: filter events containing `<@YOUR_ID>`.

---

## 9. Granola Integration (Phase 5)

* Settings key `GRANOLA_DB_PATH`.
* Script reads SQLite `notes` table, hashes content, inserts messages.

---

## 10. Embeddings

* Use Sentence‑Transformers model `BAAI/bge-small-en-v1.5` via HuggingFace Inference link: [https://huggingface.co/BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5). Hugging Face key to be picked up from .env
* Background Celery task generates `content_vector` / `summary_embedding` after write.

## 11. Local PostgreSQL + pgvector

```bash
createdb tasuke
psql -d tasuke -c "CREATE EXTENSION IF NOT EXISTS \"pgvector\";"
```

\--- + pgvector

```bash
createdb tasuke
psql -d tasuke -c "CREATE EXTENSION IF NOT EXISTS \"pgvector\";"
```

---
