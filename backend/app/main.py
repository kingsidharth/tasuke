from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.threads import router as threads_router
import threading
from backend.app.integrations.slack import start_slack_listener

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(threads_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
def startup_event():
    threading.Thread(target=start_slack_listener, daemon=True).start() 