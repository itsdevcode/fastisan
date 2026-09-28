from pathlib import Path

from fastisan.generators.model.sqlalchemy import SQLAlchemyModelGenerator


def generate_model(name: str, orm: str) -> Path:
    if orm == "sqlalchemy":
        return SQLAlchemyModelGenerator().generate(name)

    if orm == "none":
        message = (
            "Model generation requires an ORM. Current project ORM is set to 'none'."
        )
        raise ValueError(message)

    raise ValueError(f"Unsupported ORM: {orm}")
