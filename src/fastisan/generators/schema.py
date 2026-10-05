from pathlib import Path

from fastisan.generators.base import BaseGenerator
from fastisan.utils.naming import to_pascal_case, to_snake_case
from fastisan.specs import FieldSpec


class SchemaGenerator:
    def __init__(self) -> None:
        self.generator = BaseGenerator()

    def generate(self, name: str, fields: tuple[FieldSpec, ...] | None = None) -> Path:
        class_name = to_pascal_case(name)
        snake_name = to_snake_case(class_name)

        destination = Path.cwd() / "app" / "schemas" / f"{snake_name}.py"

        if fields is None:
            fields = ()

        mapped_fields = []
        for field in fields:
            mapped_fields.append({
                "name": field.name,
                "python_type": field.type,
                "nullable": field.nullable,
            })

        return self.generator.generate(
            template_name="schema.py.j2",
            destination=destination,
            context={
                "name": class_name,
                "fields": mapped_fields,
            },
        )


def generate_schema(name: str, fields: tuple[FieldSpec, ...] | None = None) -> Path:
    return SchemaGenerator().generate(name, fields=fields)