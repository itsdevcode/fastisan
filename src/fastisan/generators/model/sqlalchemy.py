from pathlib import Path

from fastisan.generators.base import BaseGenerator
from fastisan.utils.naming import (
    to_pascal_case,
    to_snake_case,
    to_table_name,
)
from fastisan.specs import FieldSpec


class SQLAlchemyModelGenerator:
    def __init__(self) -> None:
        self.generator = BaseGenerator()

    def generate(self, name: str, fields: tuple[FieldSpec, ...] | None = None) -> Path:
        class_name = to_pascal_case(name)
        snake_name = to_snake_case(class_name)
        table_name = to_table_name(class_name)

        destination = Path.cwd() / "app" / "models" / f"{snake_name}.py"

        if fields is None:
            fields = ()

        type_mapping = {
            "str": "String",
            "int": "Integer",
            "float": "Float",
            "bool": "Boolean",
            "datetime": "DateTime",
        }

        sqlalchemy_imports = {"Integer", "DateTime", "func"}
        mapped_fields = []

        for field in fields:
            sqla_type = type_mapping[field.type]
            sqlalchemy_imports.add(sqla_type)
            mapped_fields.append({
                "name": field.name,
                "python_type": field.type,
                "sqlalchemy_type": sqla_type,
                "nullable": field.nullable,
            })

        sorted_imports = sorted(list(sqlalchemy_imports))
        imports_str = ", ".join(sorted_imports)

        return self.generator.generate(
            template_name="models/sqlalchemy.py.j2",
            destination=destination,
            context={
                "name": class_name,
                "snake_name": snake_name,
                "table_name": table_name,
                "fields": mapped_fields,
                "sqlalchemy_imports": imports_str,
            },
        )
