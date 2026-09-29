from pathlib import Path

from fastisan.generators.base import BaseGenerator
from fastisan.utils.naming import to_pascal_case, to_snake_case


class ServiceGenerator:
    def __init__(self) -> None:
        self.generator = BaseGenerator()

    def generate(self, name: str) -> Path:
        class_name = to_pascal_case(name)
        snake_name = to_snake_case(class_name)

        destination = Path.cwd() / "app" / "services" / f"{snake_name}.py"
        schema_path = Path.cwd() / "app" / "schemas" / f"{snake_name}.py"
        schema_exists = schema_path.exists()

        return self.generator.generate(
            template_name="service.py.j2",
            destination=destination,
            context={
                "name": class_name,
                "snake_name": snake_name,
                "schema_exists": schema_exists,
            },
        )


def generate_service(name: str) -> Path:
    return ServiceGenerator().generate(name)
