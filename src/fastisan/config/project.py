from pathlib import Path
from typing import TypedDict, cast
import tomli


CONFIG_FILENAME = "fastisan.toml"

SUPPORTED_ORMS = {
    "sqlalchemy",
    "none",
}


class ProjectConfig(TypedDict):
    orm: str


class FastisanConfig(TypedDict):
    project: ProjectConfig


def get_config_path() -> Path:
    return Path.cwd() / CONFIG_FILENAME


def create_project_config(orm: str) -> Path:
    if orm not in SUPPORTED_ORMS:
        raise ValueError(f"Unsupported ORM: {orm}")

    config_path = get_config_path()

    if config_path.exists():
        raise FileExistsError(
            f"Fastisan project already initialized: {config_path}"
        )

    content = f'[project]\norm = "{orm}"\n'

    _ = config_path.write_text(content, encoding="utf-8")

    return config_path


def read_project_config() -> FastisanConfig:
    config_path = get_config_path()

    if not config_path.exists():
        raise FileNotFoundError(
            "Fastisan project is not initialized. Run `fastisan init` first."
        )

    with config_path.open("rb") as file:
        config = tomli.load(file)

    project = config.get("project")

    if not isinstance(project, dict):
        raise ValueError(
            "Missing [project] section in fastisan.toml"
        )

    project_config = cast(dict[str, object], project)
    orm = project_config.get("orm")

    if not isinstance(orm, str):
        raise ValueError(
            "Missing or invalid ORM in fastisan.toml"
        )

    if orm not in SUPPORTED_ORMS:
        raise ValueError(
            f"Unsupported ORM in fastisan.toml: {orm}"
        )

    return {
        "project": {
            "orm": orm,
        }
    }