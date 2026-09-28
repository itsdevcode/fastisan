from pathlib import Path

from fastisan.generators.base import BaseGenerator
from fastisan.utils.naming import to_snake_case, to_table_name


class SQLAlchemyModelGenerator:
    def __init__(self) -> None:
        self.generator = BaseGenerator()

    def generate(self, name: str) -> Path:
        snake_name = to_snake_case(name)
        table_name = to_table_name(name)

        destination = Path.cwd() / "app" / "models" / f"{snake_name}.py"

        return self.generator.generate(
            template_name="models/sqlalchemy.py.j2",
            destination=destination,
            context={
                "name": name,
                "snake_name": snake_name,
                "table_name": table_name,
            },
        )
