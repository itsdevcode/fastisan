from pathlib import Path

import pytest
from typer.testing import CliRunner

from fastisan.cli import app


runner = CliRunner()


def test_init_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        ["init"],
        input="1\n",
    )

    assert result.exit_code == 0
    assert "Fastisan initialized" in result.stdout

    config_path = tmp_path / "fastisan.toml"

    assert config_path.exists()
    assert 'orm = "sqlalchemy"' in config_path.read_text(
        encoding="utf-8"
    )
    base_path = tmp_path / "app" / "db" / "base.py"

    assert base_path.exists()

    base_content = base_path.read_text(encoding="utf-8")
    assert "class Base(DeclarativeBase):" in base_content


def test_init_command_does_not_overwrite(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    first_result = runner.invoke(
        app,
        ["init"],
        input="1\n",
    )

    assert first_result.exit_code == 0

    second_result = runner.invoke(
        app,
        ["init"],
        input="1\n",
    )

    assert second_result.exit_code == 1
    assert "already initialized" in second_result.output

def test_make_model_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    init_result = runner.invoke(app, ["init"], input="1\n")
    assert init_result.exit_code == 0

    result = runner.invoke(app, ["make:model", "User"])

    assert result.exit_code == 0
    assert "Model created" in result.stdout

    model_path = tmp_path / "app" / "models" / "user.py"

    assert model_path.exists()
    assert "class User(Base):" in model_path.read_text(encoding="utf-8")


def test_make_model_requires_initialized_project(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["make:model", "User"])

    assert result.exit_code == 1
    assert "not initialized" in result.output


def test_make_model_rejects_project_without_orm(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    init_result = runner.invoke(app, ["init"], input="2\n")
    assert init_result.exit_code == 0

    result = runner.invoke(app, ["make:model", "User"])

    assert result.exit_code == 1
    assert "requires an ORM" in result.output

def test_init_without_orm_does_not_create_database_foundation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"], input="2\n")

    assert result.exit_code == 0
    assert (tmp_path / "fastisan.toml").exists()
    assert not (tmp_path / "app" / "db" / "base.py").exists()

def test_make_schema_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["make:schema", "User"])

    assert result.exit_code == 0
    assert "Schema created" in result.stdout

    schema_path = tmp_path / "app" / "schemas" / "user.py"

    assert schema_path.exists()

    content = schema_path.read_text(encoding="utf-8")
    assert "class UserBase(BaseModel):" in content
    assert "class UserCreate(UserBase):" in content
    assert "class UserUpdate(UserBase):" in content
    assert "class UserResponse(UserBase):" in content

def test_make_schema_command_does_not_overwrite(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    first_result = runner.invoke(app, ["make:schema", "User"])

    assert first_result.exit_code == 0

    second_result = runner.invoke(app, ["make:schema", "User"])

    assert second_result.exit_code == 1
    assert "File already exists" in second_result.output


def test_make_service_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["make:service", "User"])

    assert result.exit_code == 0
    assert "Service created" in result.stdout

    service_path = tmp_path / "app" / "services" / "user.py"

    assert service_path.exists()

    content = service_path.read_text(encoding="utf-8")
    assert "class UserService:" in content


def test_make_service_command_does_not_overwrite(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    first_result = runner.invoke(app, ["make:service", "User"])

    assert first_result.exit_code == 0

    second_result = runner.invoke(app, ["make:service", "User"])

    assert second_result.exit_code == 1
    assert "File already exists" in second_result.output
