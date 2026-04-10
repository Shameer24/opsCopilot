# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "opsCopilot"
    ENV: str = "dev"
    API_PREFIX: str = "/api"

    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # OpenAI (only used if you explicitly set providers to openai)
    OPENAI_API_KEY: str | None = None
    CHAT_MODEL: str = "gpt-4.1-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Embeddings config
    EMBEDDINGS_PROVIDER: str = "local"  # "local" or "openai"
    LOCAL_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM_TARGET: int = 384

    # LLM config
    LLM_PROVIDER: str = "ollama"  # "ollama" or "local" or "openai"
    OLLAMA_BASE_URL: str = "http://host.docker.internal:11434"
    
    OLLAMA_MODEL: str = "llama3.1"

    DEV_USER_ID: str = "87240e30-e021-469b-ad0e-2b1c2ed4bbd0"

    UPLOAD_DIR: str = "./.data/uploads"
    TOP_K: int = 6
    MIN_SCORE: float = 0.10
    MAX_UPLOAD_MB: int = 25

    RL_ASK_PER_MINUTE: int = 30
    RL_UPLOAD_PER_MINUTE: int = 10

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"


settings = Settings()