from pathlib import Path

from fastisan.generators.base import BaseGenerator
from fastisan.utils.naming import to_pascal_case, to_snake_case


class MiddlewareGenerator:
    def __init__(self) -> None:
        self.generator = BaseGenerator()

    def generate(self, name: str) -> Path:
        class_name = to_pascal_case(name)
        if class_name.endswith("Middleware"):
            class_name = class_name[:-10]

        snake_name = to_snake_case(class_name)

        destination = Path.cwd() / "app" / "middleware" / f"{snake_name}.py"

        return self.generator.generate(
            template_name="middleware.py.j2",
            destination=destination,
            context={
                "name": class_name,
                "snake_name": snake_name,
            },
        )


def generate_middleware(name: str) -> Path:
    return MiddlewareGenerator().generate(name)
