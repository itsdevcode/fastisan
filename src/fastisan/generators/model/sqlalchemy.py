from pathlib import Path

from fastisan.generators.base import BaseGenerator
from fastisan.utils.naming import (
    to_pascal_case,
    to_snake_case,
    to_table_name,
)


class SQLAlchemyModelGenerator:
    def __init__(self) -> None:
        self.generator = BaseGenerator()

    def generate(self, name: str) -> Path:
        class_name = to_pascal_case(name)
        snake_name = to_snake_case(class_name)
        table_name = to_table_name(class_name)

        destination = Path.cwd() / "app" / "models" / f"{snake_name}.py"

        return self.generator.generate(
            template_name="models/sqlalchemy.py.j2",
            destination=destination,
            context={
                "name": class_name,
                "snake_name": snake_name,
                "table_name": table_name,
            },
        )
