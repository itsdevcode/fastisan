from pathlib import Path

from fastisan.generators.model.factory import generate_model
from fastisan.generators.repository import generate_repository
from fastisan.generators.router import generate_router
from fastisan.generators.schema import generate_schema
from fastisan.generators.service import generate_service
from fastisan.utils.naming import to_pascal_case, to_snake_case
from fastisan.specs import ResourceSpec


class ResourceGenerator:
    def generate(self, resource_spec: str | ResourceSpec, orm: str) -> list[Path]:
        if isinstance(resource_spec, str):
            resource_spec = ResourceSpec(name=resource_spec, fields=())

        if orm == "none":
            raise ValueError(
                "Resource generation requires an ORM. Current project ORM is set to 'none'."
            )
        if orm != "sqlalchemy":
            raise ValueError(f"Unsupported ORM: {orm}")

        class_name = to_pascal_case(resource_spec.name)
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
        paths.append(generate_model(resource_spec.name, orm, fields=resource_spec.fields))
        paths.append(generate_schema(resource_spec.name, fields=resource_spec.fields))
        paths.append(generate_repository(resource_spec.name, orm))
        paths.append(generate_service(resource_spec.name))
        paths.append(generate_router(resource_spec.name))
        return paths


def generate_resource(resource_spec: str | ResourceSpec, orm: str) -> list[Path]:
    return ResourceGenerator().generate(resource_spec, orm)
