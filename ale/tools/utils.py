import json

from pydantic import BaseModel


def get_pydantic_schema(
    model: BaseModel, include_fields: list[str] = None
) -> str:
    """Generates model schema in json string.

    It focuses only on the requested fields. These instructions are typically
    used to guide language models in structuring their responses.

    Args:
        model (BaseModel): A Pydantic model class that defines the structure
            and validation rules for the output format.
        include_fields (list[str]): A list of field names from the model that
            should be included in the formatting instructions. Default is None.
            Only these specified fields will be described in the output.


    Returns:
        str: model schema

    Example:
        >>> class Person(BaseModel):
        ...     name: str
        ...     age: int
        ...     email: str
        >>> instructions = get_pydantic_format_instructions(
        ...     Person, ["name", "age"]
        ... )
    """
    schema = dict(model.model_json_schema().items())

    # remove unnecessary fields
    srinked_schema = schema.copy()
    if "title" in srinked_schema:
        del srinked_schema["title"]
    if "type" in srinked_schema:
        del srinked_schema["type"]

    if include_fields:
        for field in srinked_schema["properties"].copy():
            if field not in include_fields:
                del srinked_schema["properties"][field]

    schema_str = json.dumps(srinked_schema, ensure_ascii=False, indent=2)
    return schema_str
