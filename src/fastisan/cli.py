from typing import cast
import typer
from fastisan.config.project import (
    create_project_config,
    get_config_path,
    read_project_config,
)
from fastisan.generators.database.factory import (
    generate_database_foundation,
)
from fastisan.generators.model.factory import generate_model
from fastisan.generators.router import generate_router
from fastisan.generators.schema import generate_schema
from fastisan.generators.service import generate_service

app = typer.Typer()
ORM_OPTIONS = {
    "1": "sqlalchemy",
    "2": "none",
}

@app.command("init")
def init_project() -> None:
    """Initialize Fastisan in the current project."""
    typer.echo("Initialize Fastisan")
    typer.echo("")
    typer.echo("Select your ORM:")
    typer.echo("1. SQLAlchemy")
    typer.echo("2. None")

    choice = cast(
        str,
        typer.prompt("ORM", default="1"),
    )
    orm = ORM_OPTIONS.get(choice)

    if orm is None:
        typer.echo("Error: Invalid ORM selection.", err=True)
        raise typer.Exit(code=1)

    config_path = get_config_path()

    if config_path.exists():
        typer.echo(
            f"Error: Fastisan project already initialized: {config_path}",
            err=True,
        )
        raise typer.Exit(code=1)

    try:
        _ = generate_database_foundation(orm)
        config_path = create_project_config(orm)
    except FileExistsError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Fastisan initialized: {config_path}")

@app.callback()
def main() -> None:
    """Fastisan - CLI for FastAPI development."""
    pass

@app.command("make:router")
def make_router(name: str) -> None:
    """Create a new FastAPI router."""
    try:
        file_path = generate_router(name)
    except FileExistsError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Router created: {file_path}")

@app.command("make:model")
def make_model(name: str) -> None:
    """Create a new model using the configured ORM."""
    try:
        config = read_project_config()
        orm = config["project"]["orm"]
        file_path = generate_model(name, orm)
    except (FileNotFoundError, FileExistsError, ValueError) as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Model created: {file_path}")


@app.command("make:schema")
def make_schema(name: str) -> None:
    """Create a new Pydantic schema."""
    try:
        file_path = generate_schema(name)
    except FileExistsError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Schema created: {file_path}")


@app.command("make:service")
def make_service(name: str) -> None:
    """Create a new service class."""
    try:
        file_path = generate_service(name)
    except FileExistsError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Service created: {file_path}")