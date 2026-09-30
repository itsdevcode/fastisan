from pathlib import Path

from fastisan.generators.repository.sqlalchemy import SQLAlchemyRepositoryGenerator


def generate_repository(name: str, orm: str) -> Path:
    if orm == "sqlalchemy":
        return SQLAlchemyRepositoryGenerator().generate(name)

    if orm == "none":
        message = (
            "Repository generation requires an ORM. Current project ORM is set to 'none'."
        )
        raise ValueError(message)

    raise ValueError(f"Unsupported ORM: {orm}")
