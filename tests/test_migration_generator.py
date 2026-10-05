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

def test_alembic_generator_orm_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    
    paths = generate_migration_foundation("none")
    assert len(paths) == 0

def test_alembic_generator_conflicts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    
    (tmp_path / "alembic.ini").write_text("")
    
    with pytest.raises(FileExistsError, match="Migration foundation component already exists: alembic.ini"):
        generate_migration_foundation("sqlalchemy")
