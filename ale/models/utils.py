from typing import Any

from pydantic import BaseModel, Field, create_model


def map_json_type_to_python(type_str: str, schema: dict = None, **kwargs):
    """Map JSON schema type to Python type.

    Args:
        type_str (str): JSON schema type string
        schema (dict): Optional schema for complex types (e.g., arrays)


    Returns:
        type: Corresponding Python type
    """
    type_mapping = {
        'string': str,
        'integer': int,
        'number': float,
        'boolean': bool,
    }

    if type_str in type_mapping:
        return type_mapping[type_str]

    if type_str == 'array':
        if schema and 'items' in schema:
            item_type = map_json_type_to_python(
                schema['items'].get('type', 'string'),
                schema['items']
            )
            return list[item_type]
        return list

    if type_str == 'object' and "object_name" in kwargs:
        return kwargs["object_name"]
    else:
        return dict

    return Any


def create_dynamic_model(
    model_name: str, json_schema: dict[str, Any]
) -> BaseModel:
    """Dynamically create a Pydantic model from an enhanced JSON schema.

    Expected schema structure:
    {
        'field_name': {
            'type': 'string',
            'description': 'Field description',
            'default': 'Optional default value',
        },
        'nested_field': {
            'type': 'object',
            'description': 'A nested object',
            'properties': {
                'sub_field': {
                    'type': 'string',
                    'description': 'Sub field description'
                }
            }
        },
        'array_field': {
            'type': 'array',
            'description': 'An array field',
            'items': {
                'type': 'object',
                'properties': {
                    'item_field': {
                        'type': 'string',
                        'description': 'Item field'
                    }
                }
            }
        }
    }
    `description` is mandatory for LLM returning structured output.

    Args:
        json_schema (dict): A dictionary representing the model's schema

    Returns:
        type: A dynamically created Pydantic model
    """
    # Prepare fields for create_model
    fields = {}
    for field_name, field_info in json_schema.items():
        # Determine field type
        field_type_str = map_json_type_to_python(
            field_info.get('type', 'string')
        )

        # Handle nested objects
        if field_type_str == 'object' and 'properties' in field_info:
            # Create a nested model
            nested_model_name = f"{model_name}{field_name.capitalize()}"
            field_type = create_dynamic_model(
                nested_model_name, field_info['properties']
            )
            print(field_type)
        # Handle arrays with nested objects
        elif field_type_str == 'array' and 'items' in field_info:
            items_schema = field_info['items']
            items_type = items_schema.get('type', 'string')

            if items_type == 'object' and 'properties' in items_schema:
                # Create a model for array items
                item_model_name = f"{model_name}_{field_name.capitalize()}Item"
                item_model = create_dynamic_model(
                    item_model_name, items_schema['properties']
                )
                field_type = list[item_model]
            else:
                # Simple array type
                field_type = map_json_type_to_python(
                    field_type_str, field_info
                )
        else:
            # Regular field type
            field_type = map_json_type_to_python(
                field_type_str, field_info, object_name=model_name
            )

        # Handle description
        description = field_info.get('description', '')
        field_value = Field(
            default=field_info.get('default', ""),
            description=description
        )

        # Store the field definition
        fields[field_name] = (field_type, field_value)

    # Dynamically create the Pydantic model
    model: BaseModel = create_model(model_name, **fields)
    return model
