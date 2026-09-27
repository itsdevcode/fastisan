from pathlib import Path

from fastisan.generators.base import BaseGenerator
from fastisan.utils.naming import to_snake_case


def generate_router(name: str) -> Path:
    snake_name = to_snake_case(name)

    destination = (
        Path.cwd()
        / "app"
        / "routers"
        / f"{snake_name}.py"
    )

    generator = BaseGenerator()

    return generator.generate(
        template_name="router.py.j2",
        destination=destination,
        context={
            "name": name,
            "snake_name": snake_name,
        },
    )