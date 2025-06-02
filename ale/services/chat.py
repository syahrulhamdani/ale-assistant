from typing import Annotated, TypedDict

from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from ale.tools import multiply


class State(MessagesState):
    document: list[str]


class Agent:
    def __init__(self):
        self.llm = init_chat_model("gemini-2.0-flash-lite").bind_tools(
            [multiply]
        )
        self.memory = MemorySaver()
        self.tool_node = ToolNode([multiply])

        builder = StateGraph(State)
        builder.add_node("chatbot", self.chat)
        builder.add_node("tools", self.tool_node)
        builder.add_edge(START, "chatbot")
        builder.add_conditional_edges(
            "chatbot", self.is_back_to_chat, ["tools", END]
        )
        builder.add_edge("tools", "chatbot")
        builder.add_edge("chatbot", END)
        self.graph = builder.compile(checkpointer=self.memory)

    def is_back_to_chat(self,state: State):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    def chat(self, state: State):
        return {"messages": [self.llm.invoke(state["messages"])]}

    def invoke(self, query: str):
        resp = self.graph.invoke(
            {"messages": [{"role": "user", "content": query}]},
            {"configurable": {"thread_id": "2105"}},
        )
        return resp
