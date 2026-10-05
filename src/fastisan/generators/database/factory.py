from pathlib import Path

from fastisan.generators.database.sqlalchemy import (
    SQLAlchemyDatabaseGenerator,
)


def generate_database_foundation(orm: str) -> list[Path] | None:
    if orm == "sqlalchemy":
        return SQLAlchemyDatabaseGenerator().generate()

    if orm == "none":
        return None

    raise ValueError(f"Unsupported ORM: {orm}")
