from pathlib import Path
from fastisan.generators.base import BaseGenerator
from fastisan.generators.registry import regenerate_router_registry


class ApplicationGenerator:
    def __init__(self) -> None:
        self.generator = BaseGenerator()

    def generate(self, orm: str) -> list[Path]:
        app_dir = Path.cwd() / "app"
        
        main_destination = app_dir / "main.py"
        registry_destination = app_dir / "routers" / "registry.py"

        conflicts = [p for p in (main_destination, registry_destination) if p.exists()]

        if orm == "sqlalchemy":
            alembic_ini = Path.cwd() / "alembic.ini"
            env_py = Path.cwd() / "migrations" / "env.py"
            conflicts.extend([p for p in (alembic_ini, env_py) if p.exists()])

        if conflicts:
            conflict_names = ", ".join(str(p) for p in conflicts)
            raise FileExistsError(f"Application foundation components already exist: {conflict_names}")
            
        paths: list[Path] = []
        
        from fastisan.generators.database.factory import generate_database_foundation
        db_paths = generate_database_foundation(orm)
        if db_paths:
            paths.extend(db_paths)
        
        paths.append(self.generator.generate(
            template_name="main.py.j2",
            destination=main_destination,
            context={},
        ))
        
        paths.append(regenerate_router_registry())
        
        packages = ["", "models", "schemas", "repositories", "services", "routers"]
        if orm == "sqlalchemy":
            packages.append("db")
            
        for pkg in packages:
            pkg_path = app_dir / pkg if pkg else app_dir
            pkg_path.mkdir(parents=True, exist_ok=True)
            init_file = pkg_path / "__init__.py"
            if not init_file.exists():
                _ = init_file.write_text("", encoding="utf-8")
                paths.append(init_file)
                
        if orm == "sqlalchemy":
            from fastisan.generators.migration.alembic import generate_migration_foundation
            from fastisan.generators.model_registry import regenerate_model_registry
            paths.extend(generate_migration_foundation(orm))
            paths.append(regenerate_model_registry())

        return paths
