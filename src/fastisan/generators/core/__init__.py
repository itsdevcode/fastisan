from pathlib import Path

from fastisan.generators.base import BaseGenerator


class CoreConfigGenerator:
    def __init__(self) -> None:
        self.generator = BaseGenerator()

    def generate(self) -> list[Path]:
        core_dir = Path.cwd() / "app" / "core"
        config_destination = core_dir / "config.py"
        env_example_destination = Path.cwd() / ".env.example"

        conflicts = [p for p in (config_destination,) if p.exists()]
        if conflicts:
            conflict_names = ", ".join(str(p) for p in conflicts)
            raise FileExistsError(
                f"Core configuration components already exist: {conflict_names}"
            )

        paths: list[Path] = []

        paths.append(
            self.generator.generate(
                template_name="core/config.py.j2",
                destination=config_destination,
                context={},
            )
        )

        # Generate __init__.py for core package
        init_file = core_dir / "__init__.py"
        if not init_file.exists():
            _ = init_file.write_text("", encoding="utf-8")
            paths.append(init_file)

        # Generate .env.example (don't raise if it already exists — just skip)
        if not env_example_destination.exists():
            paths.append(
                self.generator.generate(
                    template_name="env.example.j2",
                    destination=env_example_destination,
                    context={},
                )
            )

        return paths
