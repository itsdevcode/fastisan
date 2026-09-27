from pathlib import Path

from jinja2 import Environment, PackageLoader

from fastisan.utils.naming import to_snake_case


def generate_router(name: str) -> Path:
    snake_name = to_snake_case(name)

    router_directory = Path.cwd() / "app" / "routers"
    router_directory.mkdir(parents=True, exist_ok=True)

    file_path = router_directory / f"{snake_name}.py"

    if file_path.exists():
        raise FileExistsError(f"Router already exists: {file_path}")

    environment = Environment(
        loader=PackageLoader("fastisan", "templates"),
        autoescape=False,
        keep_trailing_newline=True,
    )

    template = environment.get_template("router.py.j2")

    content = template.render(
        name=name,
        snake_name=snake_name,
    )

    _ = file_path.write_text(content, encoding="utf-8")

    return file_path