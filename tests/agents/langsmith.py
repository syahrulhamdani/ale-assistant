import json
from os.path import exists

from langsmith import Client


ls = Client()


def is_dataset_exists(dataset_name: str, client: Client = ls) -> bool:
    """Check if the dataset exists in LangSmith.

    Args:
        dataset_name (str): The name of the dataset.

    Returns:
        bool: True if the dataset exists, False otherwise.
    """
    return any(client.list_datasets(dataset_name=dataset_name))


def load_eval_data_from_local(filepath: str) -> dict:
    """Load evaluation data from a local file.

    Args:
        filepath (str): The path to the evaluation data file with JSON format.

    Returns:
        dict: The evaluation data as a dictionary.
    """
    if not exists(filepath):
        raise FileNotFoundError(f"File {filepath} not found.")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
