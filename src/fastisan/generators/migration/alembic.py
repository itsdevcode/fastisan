from pathlib import Path
from fastisan.generators.base import BaseGenerator

class AlembicGenerator:
    def __init__(self) -> None:
        self.generator = BaseGenerator()

    def generate(self) -> list[Path]:
        cwd = Path.cwd()
        alembic_ini = cwd / "alembic.ini"
        migrations_dir = cwd / "migrations"
        env_py = migrations_dir / "env.py"
        script_mako = migrations_dir / "script.py.mako"
        versions_dir = migrations_dir / "versions"
        gitkeep = versions_dir / ".gitkeep"

        conflicts = [p for p in (alembic_ini, env_py, script_mako) if p.exists()]
        if conflicts:
            conflict_names = ", ".join(p.name for p in conflicts)
            raise FileExistsError(f"Migration foundation component already exists: {conflict_names}")

        migrations_dir.mkdir(parents=True, exist_ok=True)
        versions_dir.mkdir(parents=True, exist_ok=True)
        
        if not gitkeep.exists():
            _ = gitkeep.write_text("", encoding="utf-8")

        paths: list[Path] = [gitkeep]

        paths.append(self.generator.generate(
            template_name="alembic.ini.j2",
            destination=alembic_ini,
            context={},
        ))

        paths.append(self.generator.generate(
            template_name="migrations/env.py.j2",
            destination=env_py,
            context={},
        ))

        paths.append(self.generator.generate(
            template_name="migrations/script.py.mako.j2",
            destination=script_mako,
            context={},
        ))

        return paths

def generate_migration_foundation(orm: str) -> list[Path]:
    if orm == "sqlalchemy":
        return AlembicGenerator().generate()
    return []
