import pytest
from pathlib import Path
from fastisan.generators.migration.alembic import generate_migration_foundation, AlembicGenerator

def test_alembic_generator(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    paths = generate_migration_foundation("sqlalchemy")

    assert len(paths) == 4
    assert (tmp_path / "alembic.ini").exists()
    assert (tmp_path / "migrations" / "env.py").exists()
    assert (tmp_path / "migrations" / "script.py.mako").exists()
    assert (tmp_path / "migrations" / "versions" / ".gitkeep").exists()

    alembic_ini_content = (tmp_path / "alembic.ini").read_text(encoding="utf-8")
    assert "postgresql+asyncpg://user:pass@localhost/db" not in alembic_ini_content
    assert "sqlalchemy.url = \n" in alembic_ini_content
    assert "script_location = migrations" in alembic_ini_content

    env_content = (tmp_path / "migrations" / "env.py").read_text(encoding="utf-8")
    assert 'database_url = os.environ["DATABASE_URL"]' in env_content
    assert 'database_url.replace("%", "%%")' in env_content

def test_alembic_generator_orm_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    paths = generate_migration_foundation("none")
    assert len(paths) == 0

def test_alembic_generator_conflicts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / "alembic.ini").write_text("")

    with pytest.raises(FileExistsError, match="Migration foundation component already exists: alembic.ini"):
        generate_migration_foundation("sqlalchemy")

def test_alembic_generator_script_mako_conflict(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    (migrations_dir / "script.py.mako").touch()

    with pytest.raises(FileExistsError, match="Migration foundation component already exists: script.py.mako"):
        generate_migration_foundation("sqlalchemy")

    assert not (tmp_path / "alembic.ini").exists()
    assert not (tmp_path / "migrations" / "env.py").exists()
    assert not (tmp_path / "migrations" / "versions").exists()
