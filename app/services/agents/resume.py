"""Resume Agent."""

import logging
import json
from dataclasses import dataclass, field

from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.messages import SystemMessage
from langchain_core.tools import Tool
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from app.models.resume import ResumeData, ResumeState
from app.services.tools.resume import tool_generate_resume

_LOGGER = logging.getLogger(__name__)


@dataclass
class ResumeAgent:
    model: BaseLanguageModel
    system_prompt: str = field(
        default=(
            "You're a Resume agent. Your task is to help to generate resume, "
            "interactively based on the users query while adhering to the "
            "required contents.\n"
        )
    )
    memory: MemorySaver = field(default_factory=MemorySaver)

    def __post_init__(self):
        self.graph = StateGraph(ResumeState)
        self.graph.add_node("extract_content", self.node_extract_content)
        # self.graph.add_node("validate_content", self.node_validate_content)
        self.graph.add_node("generate_resume", tool_generate_resume)
        self.graph.add_node("ask_more", self.node_ask_more)

        self.graph.add_edge(START, "extract_content")
        self.graph.add_conditional_edges(
            "extract_content",
            self.node_validate_content,
            {"missing": "ask_more", "complete": "generate_resume"},
        )
        self.graph.add_edge("ask_more", END)
        self.graph.add_edge("generate_resume", END)
        # self.agent = self.graph.compile(checkpointer=self.memory)
        self.agent = self.graph.compile()

    def node_extract_content(self, state: ResumeState):
        """Extract resume data."""
        messages = state["messages"]
        response = self.model.with_structured_output(
            ResumeData, include_raw=True
        ).invoke(
            [
                SystemMessage(
                    content=(
                        "Extract relevant fields needed for generating resume"
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
            # "messages": [
            #     {"role": "system", "content": json.dumps(resume_data)}
            # ],
            "missing_fields": missing_fields,
            "data": ResumeData(**resume_data),
        }

    def node_ask_more(self, state: ResumeState):
        """Ask user for more information."""
        messages = state["messages"]
        response = self.model.invoke(
            [SystemMessage(content=self.system_prompt)] + messages
        )
        return {"messages": [response]}

    def node_validate_content(self, state: ResumeState) -> str:
        """Validate resume data."""
        if state["missing_fields"]:
            _LOGGER.info("Missing fields: %s", state["missing_fields"])
            return "missing"

        _LOGGER.info("Resume data is complete. Routing to resume generator")
        return "complete"
