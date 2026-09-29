from pathlib import Path

from fastisan.generators.base import BaseGenerator
from fastisan.utils.naming import to_pascal_case, to_snake_case


class SchemaGenerator:
    def __init__(self) -> None:
        self.generator = BaseGenerator()

    def generate(self, name: str) -> Path:
        class_name = to_pascal_case(name)
        snake_name = to_snake_case(class_name)

        destination = Path.cwd() / "app" / "schemas" / f"{snake_name}.py"

        return self.generator.generate(
            template_name="schema.py.j2",
            destination=destination,
            context={
                "name": class_name,
            },
        )


def generate_schema(name: str) -> Path:
    return SchemaGenerator().generate(name)