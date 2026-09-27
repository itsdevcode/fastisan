from typing import cast
import typer
from fastisan.generators.router import generate_router
from fastisan.config.project import create_project_config

app = typer.Typer()
ORM_OPTIONS = {
    "1": "sqlalchemy",
    "2": "sqlmodel",
    "3": "tortoise",
    "4": "none",
}

@app.command("init")
def init_project() -> None:
    """Initialize Fastisan in the current project."""

    typer.echo("Initialize Fastisan")
    typer.echo("")
    typer.echo("Select your ORM:")
    typer.echo("1. SQLAlchemy")
    typer.echo("2. SQLModel")
    typer.echo("3. Tortoise ORM")
    typer.echo("4. None")

    choice = cast(
        str,
        typer.prompt(
            "ORM",
            default="1",
            type=str,
        ),
    )

    orm = ORM_OPTIONS.get(choice)

    if orm is None:
        typer.echo("Error: Invalid ORM selection.", err=True)
        raise typer.Exit(code=1)

    try:
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