import os

from pydantic_settings import BaseSettings


class LLMConfig(BaseSettings):
    VERTEXAI_MODEL_NAME: str = os.getenv("VERTEXAI_MODEL_NAME",
                                         "gemini-2.0-flash")
    VERTEXAI_TEMPERATURE: float = os.getenv("VERTEXAI_TEMPERATURE", 0.0)
    VERTEXAI_MAX_OUTPUT_TOKENS: int = os.getenv("VERTEXAI_MAX_OUTPUT_TOKENS",
                                                1024)
    VERTEXAI_TOP_P: float = os.getenv("VERTEXAI_TOP_P", .3)


class Settings(LLMConfig):
    RESUME_API_PREFIX: str = os.getenv("RESUME_API_PREFIX", "/sylab/api/v1")
    RESUME_GENERATOR_URL: str = os.getenv("RESUME_GENERATOR_URL")
    RESUME_DOWNLOAD_PATH: str = os.getenv(
        "RESUME_DOWNLOAD_PATH", "resume.pdf"
    )


config = Settings()
