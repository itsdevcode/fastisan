from pathlib import Path

from fastisan.generators.base import BaseGenerator


class SQLAlchemyDatabaseGenerator:
    def __init__(self) -> None:
        self.generator = BaseGenerator()

    def generate(self) -> list[Path]:
        db_dir = Path.cwd() / "app" / "db"
        base_destination = db_dir / "base.py"
        session_destination = db_dir / "session.py"

        conflicts = [p for p in (base_destination, session_destination) if p.exists()]
        if conflicts:
            conflict_names = ", ".join(str(p) for p in conflicts)
            raise FileExistsError(f"Database foundation components already exist: {conflict_names}")

        paths: list[Path] = []
        paths.append(self.generator.generate(
            template_name="database/sqlalchemy_base.py.j2",
            destination=base_destination,
            context={},
        ))

        paths.append(self.generator.generate(
            template_name="database/sqlalchemy_session.py.j2",
            destination=session_destination,
            context={},
        ))

        return paths
