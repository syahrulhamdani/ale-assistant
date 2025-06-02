from langchain_google_vertexai import ChatVertexAI

from ale.core.config import config as c
from ale.agents.resume import ResumeAgent


def create_resume_agent():
    """Create default resume agent."""
    llm = ChatVertexAI(
        model_name=c.VERTEXAI_MODEL_NAME,
        temperature=c.VERTEXAI_TEMPERATURE,
        max_output_tokens=c.VERTEXAI_MAX_OUTPUT_TOKENS,
        top_p=c.VERTEXAI_TOP_P,
    )
    return ResumeAgent(model=llm)


resume_agent = create_resume_agent().agent


__all__ = ["resume_agent"]
