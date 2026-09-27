from pathlib import Path

from jinja2 import Environment, PackageLoader


class BaseGenerator:
    def __init__(self) -> None:
        self.environment = Environment(
            loader=PackageLoader("fastisan", "templates"),
            autoescape=False,
            keep_trailing_newline=True,
        )

    def generate(
        self,
        template_name: str,
        destination: Path,
        context: dict[str, object],
    ) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)

        if destination.exists():
            raise FileExistsError(f"File already exists: {destination}")

        template = self.environment.get_template(template_name)
        content = template.render(**context)

        _ = destination.write_text(content, encoding="utf-8")

        return destination