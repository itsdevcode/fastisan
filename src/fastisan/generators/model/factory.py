from pathlib import Path

from fastisan.generators.model.sqlalchemy import SQLAlchemyModelGenerator
from fastisan.specs import FieldSpec


def generate_model(name: str, orm: str, fields: tuple[FieldSpec, ...] | None = None) -> Path:
    if orm == "sqlalchemy":
        return SQLAlchemyModelGenerator().generate(name, fields=fields)

    if orm == "none":
        message = (
            "Model generation requires an ORM. Current project ORM is set to 'none'."
        )
        raise ValueError(message)

    raise ValueError(f"Unsupported ORM: {orm}")
