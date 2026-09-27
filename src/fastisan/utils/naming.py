import re


def to_snake_case(value: str) -> str:
    """Convert PascalCase or camelCase to snake_case."""
    value = re.sub(r"(?<!^)(?=[A-Z])", "_", value)
    return value.lower()