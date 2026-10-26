import os
from pathlib import Path
import pytest
from typer.testing import CliRunner

from fastisan.cli import app
from fastisan.generators.migration.alembic import generate_migration_foundation

runner = CliRunner()


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
    assert "sqlalchemy.url =" in alembic_ini_content
    assert "script_location = migrations" in alembic_ini_content
    assert "prepend_sys_path = ." in alembic_ini_content
    assert "[loggers]" in alembic_ini_content
    assert "[logger_alembic]" in alembic_ini_content

    env_content = (tmp_path / "migrations" / "env.py").read_text(encoding="utf-8")
    # Centralized application settings usage
    assert "from app.core.config import settings" in env_content
    assert 'settings.database_url.replace("%", "%%")' in env_content
    assert "os.environ" not in env_content
    assert "import os" not in env_content

    # Preserved components
    assert "import app.models.registry" in env_content
    assert "from app.db.base import Base" in env_content
    assert "target_metadata = Base.metadata" in env_content
    assert "async_engine_from_config" in env_content
    assert "await connectable.dispose()" in env_content


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


def test_alembic_shares_database_url_source_with_app(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"], input="1\n")
    assert result.exit_code == 0

    session_content = (tmp_path / "app" / "db" / "session.py").read_text(encoding="utf-8")
    env_content = (tmp_path / "migrations" / "env.py").read_text(encoding="utf-8")

    # Both must import settings from app.core.config
    assert "from app.core.config import settings" in session_content
    assert "from app.core.config import settings" in env_content

    # Both must reference settings.database_url
    assert "settings.database_url" in session_content
    assert "settings.database_url" in env_content

    # Neither should access os.environ directly
    assert "os.environ" not in session_content
    assert "os.environ" not in env_content


def test_alembic_url_escaping_logic() -> None:
    # Verify % escaping behavior required for Alembic ConfigParser
    raw_url = "postgresql+asyncpg://user:p%40ss%25word@localhost:5432/db%20name"
    escaped_url = raw_url.replace("%", "%%")
    assert escaped_url == "postgresql+asyncpg://user:p%%40ss%%25word@localhost:5432/db%%20name"
    assert "%%" in escaped_url


@pytest.mark.skipif(
    not os.environ.get("TEST_DATABASE_URL"),
    reason="PostgreSQL test database not available (set TEST_DATABASE_URL to enable)",
)
def test_alembic_migration_execution_postgresql(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    test_db_url = os.environ["TEST_DATABASE_URL"]
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"], input="1\n")
    assert result.exit_code == 0

    # Write .env with the test database URL
    (tmp_path / ".env").write_text(f"DATABASE_URL={test_db_url}\n", encoding="utf-8")

    import subprocess
    rev_res = subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", "test_init"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert rev_res.returncode == 0

    up_res = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert up_res.returncode == 0
