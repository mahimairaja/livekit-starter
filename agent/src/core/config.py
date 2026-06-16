import logging
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=False)

logger = logging.getLogger(__name__)


class Config(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", case_sensitive=True)

    # Identity. AGENT_NAME is also the dispatch name the frontend must request.
    AGENT_NAME: str = "assistant"
    ENV: str = "prod"
    PROJECT_NAME: str = "Voice Agent"

    # Optional error tracking.
    SENTRY_DSN: str | None = None

    # NOTE: LIVEKIT_URL / LIVEKIT_API_KEY / LIVEKIT_API_SECRET and the provider
    # keys (OPENAI_API_KEY, DEEPGRAM_API_KEY, CARTESIA_API_KEY) are read directly
    # from the environment by the LiveKit framework and plugins. They are
    # documented in .env.example; no Config fields are needed for them.


@lru_cache
def get_config() -> Config:
    return Config()


config = get_config()
