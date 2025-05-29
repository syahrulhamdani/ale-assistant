"""Unit-tests for extract content node in Resume Agent."""
import json
from typing import Iterator

from langchain_core.messages import HumanMessage
from langsmith.schemas import Dataset, Example
from loguru import logger

from app.core.config import LLMEvaluatorConfig
from tests.agents.langsmith import is_dataset_exists, load_eval_data_from_local, ls

config = LLMEvaluatorConfig()


def evals_dataset():
    """Get evals dataset for content extraction for resume agent."""
    dataset_name = config.EVAL_EXTRACT_CONTENT_DATASET_NAME
    data = load_eval_data_from_local(f"tests/data/{dataset_name}.json")

    if not is_dataset_exists(dataset_name):
        dataset: Dataset = ls.create_dataset(
            dataset_name=dataset_name,
            description="Evals dataset for content extraction for resume agent.",
        )

    if not any(ls.list_examples(dataset_name=dataset_name)):
        res = ls.create_examples(
            dataset_name=dataset_name,
            inputs=[{"messages": [HumanMessage(content=d["input"])]} for d in data],
            outputs=[json.loads(d["output"]) for d in data],
        )
        logger.info(
            f"Created dataset {dataset_name} with {res['count']} examples."
        )

    examples: Iterator[Example] = ls.list_examples(dataset_name=dataset_name)
    return examples
