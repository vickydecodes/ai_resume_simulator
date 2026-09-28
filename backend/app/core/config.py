import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Interview Simulator"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "interview_simulator"

    # LLM settings
    LLM_PROVIDER: str = "openrouter"  # 'openrouter', 'anthropic', 'openai', 'gemini', 'mock'
    LLM_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    LLM_MODEL: str = "anthropic/claude-3.5-sonnet"

    # CORS & Security
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]
    MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB

    # Scoring Weights Config
    WEIGHT_RESUME_FIT: float = 0.25
    WEIGHT_TECHNICAL_KNOWLEDGE: float = 0.35
    WEIGHT_COMMUNICATION: float = 0.15
    WEIGHT_PROBLEM_SOLVING: float = 0.15
    WEIGHT_COMPANY_AWARENESS: float = 0.10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
