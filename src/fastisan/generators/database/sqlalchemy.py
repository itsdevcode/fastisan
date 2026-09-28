from pathlib import Path

from fastisan.generators.base import BaseGenerator


class SQLAlchemyDatabaseGenerator:
    def __init__(self) -> None:
        self.generator = BaseGenerator()

    def generate(self) -> Path:
        destination = Path.cwd() / "app" / "db" / "base.py"

        return self.generator.generate(
            template_name="database/sqlalchemy_base.py.j2",
            destination=destination,
            context={},
        )
