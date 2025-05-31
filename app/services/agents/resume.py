"""Resume Agent."""

import json
import logging
from dataclasses import dataclass, field

from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.models.resume import ResumeData, ResumeState
from app.services.tools.resume import tool_generate_resume
from app.services.tools.utils import get_pydantic_schema

_LOGGER = logging.getLogger(__name__)


@dataclass
class ResumeAgent:
    """Resume agent service."""

    model: BaseLanguageModel
    system_prompt: str = field(
        default=(
            "You're a Resume agent. Your task is to help to generate resume, "
            "interactively based on the users query while adhering to the "
            "required contents. "
            "You can review what you already have with the users.\n"
            "A complete resume data must have these schema:\n"
            "{resume_schema}\n"
            "You already have the following data:\n{current_data}"
        )
    )
    extractor_prompt: str = field(
        default=(
            "Extract relevant fields needed for generating resume.\n"
        )
    )
    memory: MemorySaver = field(default_factory=MemorySaver)

    def __post_init__(self):
        self.graph = StateGraph(ResumeState)
        self.graph.add_node("extract_content", self.extract_content)
        self.graph.add_node("generate_resume", tool_generate_resume)
        self.graph.add_node("ask_more", self.ask_more)

        self.graph.add_edge(START, "extract_content")
        self.graph.add_conditional_edges(
            "extract_content",
            self.validate_content,
            {"missing": "ask_more", "complete": "generate_resume"},
        )
        self.graph.add_edge("ask_more", END)
        self.graph.add_edge("generate_resume", END)
        self.agent = self.graph.compile(checkpointer=self.memory)

    def extract_content(self, state: ResumeState):
        """Extract resume data."""
        messages = state["messages"]
        response = self.model.with_structured_output(
            ResumeData, include_raw=True
        ).invoke(
            [
                SystemMessage(
                    content=(
                        self.extractor_prompt
                        + (
                            "" if not state.get("data")
                            else f"Current resume data: {state['data']}"
                        )
                    )
                )
            ]
            + messages
        )
        resume_data = response["parsed"].model_dump()
        _LOGGER.info("Got resume data: %s", resume_data.keys())

        extracted_field = response["raw"].tool_calls[0]["args"].keys()
        missing_fields = [
            field
            for field in ResumeData.model_fields.keys()
            if field not in extracted_field
        ]

        return {
            "missing_fields": missing_fields,
            "data": ResumeData(**resume_data),
            "messages": messages,
        }

    def ask_more(self, state: ResumeState):
        """Ask user for more information."""
        system_prompt = self.system_prompt.format(
            current_data=json.dumps(state["data"].model_dump()),
            resume_schema=get_pydantic_schema(ResumeData),
        )
        response = self.model.invoke([HumanMessage(content=system_prompt)])
        return {"messages": [response]}

    def validate_content(self, state: ResumeState) -> str:
        """Validate resume data."""
        if state["missing_fields"]:
            _LOGGER.info("Missing fields: %s", state["missing_fields"])
            return "missing"

        _LOGGER.info("Resume data is complete. Routing to resume generator")
        return "complete"
