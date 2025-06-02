"""Configurations module."""
import os

from pydantic_settings import BaseSettings


class LLMEvaluatorConfig(BaseSettings):
    EVALUATOR_MODEL_NAME: str = os.getenv("EVALUATOR_MODEL_NAME",
                                          "text-davinci-003")
    EVALUATOR_TEMPERATURE: float = float(
        os.getenv("EVALUATOR_TEMPERATURE", "0.0")
    )
    EVALUATOR_MAX_OUTPUT_TOKENS: int = int(
        os.getenv("EVALUATOR_MAX_OUTPUT_TOKENS", "1024")
    )
    EVALUATOR_TOP_P: float = float(os.getenv("EVALUATOR_TOP_P", ".3"))

    EVAL_EXTRACT_CONTENT_DATASET_NAME: str = os.getenv(
        "EVAL_EXTRACT_CONTENT_DATASET_NAME", "extract_content"
    )


class LLMConfig(BaseSettings):
    VERTEXAI_MODEL_NAME: str = os.getenv("VERTEXAI_MODEL_NAME",
                                         "gemini-2.0-flash")
    VERTEXAI_TEMPERATURE: float = float(
        os.getenv("VERTEXAI_TEMPERATURE", "0.0")
    )
    VERTEXAI_MAX_OUTPUT_TOKENS: int = int(
        os.getenv("VERTEXAI_MAX_OUTPUT_TOKENS", "1024")
    )
    VERTEXAI_TOP_P: float = float(os.getenv("VERTEXAI_TOP_P", ".3"))


class Settings(LLMConfig):
    ENV: str = os.getenv("ENV", "dev")

    RESUME_API_PREFIX: str = os.getenv("RESUME_API_PREFIX", "/sylab/api/v1")
    RESUME_GENERATOR_URL: str = os.getenv("RESUME_GENERATOR_URL")
    RESUME_DOWNLOAD_PATH: str = os.getenv(
        "RESUME_DOWNLOAD_PATH", "resume.pdf"
    )


config = Settings()
