import os

class Settings:
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_DEFAULT_MODEL: str = os.getenv("OPENROUTER_DEFAULT_MODEL", "anthropic/claude-3-haiku")
    OPENROUTER_DEFAULT_TEMPERATURE: float = float(os.getenv("OPENROUTER_DEFAULT_TEMPERATURE", "0.7"))

settings = Settings() 