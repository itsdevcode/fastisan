from pathlib import Path

from fastisan.generators.base import BaseGenerator
from fastisan.utils.naming import to_pascal_case, to_snake_case, to_table_name


def generate_router(name: str) -> Path:
    class_name = to_pascal_case(name)
    snake_name = to_snake_case(class_name)
    plural_snake_name = to_table_name(class_name)

    destination = (
        Path.cwd()
        / "app"
        / "routers"
        / f"{snake_name}.py"
    )

    schema_exists = (Path.cwd() / "app" / "schemas" / f"{snake_name}.py").exists()
    service_exists = (Path.cwd() / "app" / "services" / f"{snake_name}.py").exists()
    repository_exists = (Path.cwd() / "app" / "repositories" / f"{snake_name}.py").exists()
    session_exists = (Path.cwd() / "app" / "db" / "session.py").exists()

    generator = BaseGenerator()

    return generator.generate(
        template_name="router.py.j2",
        destination=destination,
        context={
            "name": class_name,
            "snake_name": snake_name,
            "plural_snake_name": plural_snake_name,
            "schema_exists": schema_exists,
            "service_exists": service_exists,
            "repository_exists": repository_exists,
            "session_exists": session_exists,
        },
    )