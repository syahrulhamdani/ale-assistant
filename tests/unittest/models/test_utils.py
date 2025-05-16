import pytest
from pydantic import ValidationError

from app.models.utils import create_dynamic_model


def test_simple_model_creation():
    "Test createing a simple model."
    schema = {
        "name": {
            "default": "John Doe",
            "description": "Customer's name",
            "type": "string",
        },
        "title": {
            "description": "Customer's job title",
            "default": "Software Engineer",
            "type": "string",
        },
        "age": {
            "description": "Customer's age",
            "default": 30,
            "type": "integer",
        }
    }

    Customer = create_dynamic_model("Customer", schema)

    cust_1 = Customer(name="Alice", title="Consultant", age=20)
    assert cust_1.name == "Alice"
    assert cust_1.title == "Consultant"
    assert cust_1.age == 20

    cust_2 = Customer()
    assert cust_2.name == "John Doe"
    assert cust_2.title == "Software Engineer"
    assert cust_2.age == 30


def test_nested_model_creation():
    "Test creating a nested model."
    schema = {
        "name": {
            "default": "John Doe",
            "description": "Customer's name",
            "type": "string",
        },
        "title": {
            "description": "Customer's job title",
            "default": "Software Engineer",
            "type": "string",
        },
        "age": {
            "description": "Customer's age",
            "default": 30,
            "type": "integer",
        },
        "address": {
            "type": "object",
            "properties": {
                "street": {
                    "type": "string",
                    "default": "123 Main St",
                    "description": "Customer's street address",
                },
                "city": {
                    "type": "string",
                    "default": "Bandung",
                    "description": "Customer's city",
                },
                "state": {
                    "type": "string",
                    "default": "West Java",
                    "description": "Customer's state",
                },
            },
            "description": "Customer's address",
        }
    }

    Customer = create_dynamic_model("Customer", schema)

    data = {
        "name": "Alice",
        "title": "Consultant",
        "age": 20,
        "address": {
            "street": "456 Elm St",
            "city": "Semarang",
            "state": "Central Java",
        }
    }
    customer = Customer(**data)
    print(customer)
    assert customer.name == "Alice"
    assert customer.title == "Consultant"
    assert customer.age == 20
    assert customer.address.street == "456 Elm St"
    assert customer.address.city == "Semarang"
    assert customer.address.state == "Central Java"
