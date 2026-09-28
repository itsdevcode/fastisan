import re
from typing import cast

import inflect
from inflect import Word


_inflector = inflect.engine()


def to_snake_case(value: str) -> str:
    value = re.sub(r"(?<!^)(?=[A-Z])", "_", value)
    return value.lower()


def to_table_name(value: str) -> str:
    snake_name = to_snake_case(value)
    word = cast(Word, cast(object, snake_name))
    return _inflector.plural(word)

def to_pascal_case(value: str) -> str:
    parts = value.replace("-", "_").split("_")
    return "".join(part[:1].upper() + part[1:] for part in parts if part)