from pathlib import Path

from fastisan.generators.model.factory import generate_model
from fastisan.generators.repository import generate_repository
from fastisan.generators.router import generate_router
from fastisan.generators.schema import generate_schema
from fastisan.generators.service import generate_service
from fastisan.utils.naming import to_pascal_case, to_snake_case


class ResourceGenerator:
    def generate(self, name: str, orm: str) -> list[Path]:
        if orm == "none":
            raise ValueError(
                "Resource generation requires an ORM. Current project ORM is set to 'none'."
            )
        if orm != "sqlalchemy":
            raise ValueError(f"Unsupported ORM: {orm}")

        class_name = to_pascal_case(name)
        snake_name = to_snake_case(class_name)

        base_dir = Path.cwd() / "app"
        expected_paths = [
            base_dir / "models" / f"{snake_name}.py",
            base_dir / "schemas" / f"{snake_name}.py",
            base_dir / "repositories" / f"{snake_name}.py",
            base_dir / "services" / f"{snake_name}.py",
            base_dir / "routers" / f"{snake_name}.py",
        ]

        conflicts = [p for p in expected_paths if p.exists()]
        if conflicts:
            conflict_names = ", ".join(str(p) for p in conflicts)
            raise FileExistsError(f"Resource components already exist: {conflict_names}")

        paths: list[Path] = []
        paths.append(generate_model(name, orm))
        paths.append(generate_schema(name))
        paths.append(generate_repository(name, orm))
        paths.append(generate_service(name))
        paths.append(generate_router(name))
        return paths


def generate_resource(name: str, orm: str) -> list[Path]:
    return ResourceGenerator().generate(name, orm)
