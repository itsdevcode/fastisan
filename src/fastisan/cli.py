import typer
from fastisan.generators.router import generate_router

app = typer.Typer()


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