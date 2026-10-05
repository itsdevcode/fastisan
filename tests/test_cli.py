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

    session_path = tmp_path / "app" / "db" / "session.py"
    assert session_path.exists()

    session_content = session_path.read_text(encoding="utf-8")
    assert "async def get_session" in session_content
    assert "DATABASE_URL = os.environ[\"DATABASE_URL\"]" in session_content

    main_path = tmp_path / "app" / "main.py"
    assert main_path.exists()
    assert "from fastapi import FastAPI" in main_path.read_text(encoding="utf-8")

    registry_path = tmp_path / "app" / "routers" / "registry.py"
    assert registry_path.exists()
    assert "router = APIRouter()" in registry_path.read_text(encoding="utf-8")

    for pkg in ["", "models", "schemas", "repositories", "services", "routers", "db"]:
        pkg_init = tmp_path / "app" / pkg / "__init__.py" if pkg else tmp_path / "app" / "__init__.py"
        assert pkg_init.exists()

    alembic_ini_path = tmp_path / "alembic.ini"
    assert alembic_ini_path.exists()
    assert "script_location = migrations" in alembic_ini_path.read_text(encoding="utf-8")

    env_path = tmp_path / "migrations" / "env.py"
    assert env_path.exists()
    assert "import app.models.registry" in env_path.read_text(encoding="utf-8")

    script_path = tmp_path / "migrations" / "script.py.mako"
    assert script_path.exists()

    versions_path = tmp_path / "migrations" / "versions"
    assert versions_path.exists()

    model_registry_path = tmp_path / "app" / "models" / "registry.py"
    assert model_registry_path.exists()


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

def test_make_router_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    init_result = runner.invoke(app, ["init"], input="1\n")
    assert init_result.exit_code == 0

    result = runner.invoke(app, ["make:router", "User"])

    assert result.exit_code == 0
    assert "Router created" in result.stdout

    router_path = tmp_path / "app" / "routers" / "user.py"
    assert router_path.exists()

    registry_path = tmp_path / "app" / "routers" / "registry.py"
    registry_content = registry_path.read_text(encoding="utf-8")
    assert "from app.routers.user import router as user_router" in registry_content
    assert "router.include_router(user_router)" in registry_content

def test_make_router_command_uninitialized(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["make:router", "User"])

    assert result.exit_code == 0
    assert "Router created" in result.stdout

    router_path = tmp_path / "app" / "routers" / "user.py"
    assert router_path.exists()

    registry_path = tmp_path / "app" / "routers" / "registry.py"
    assert not registry_path.exists()

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

    model_registry_path = tmp_path / "app" / "models" / "registry.py"
    registry_content = model_registry_path.read_text(encoding="utf-8")
    assert "from app.models.user import User" in registry_content
    assert '"User",' in registry_content


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

    assert (tmp_path / "app" / "main.py").exists()
    assert (tmp_path / "app" / "routers" / "registry.py").exists()
    assert not (tmp_path / "alembic.ini").exists()
    assert not (tmp_path / "migrations" / "env.py").exists()
    assert not (tmp_path / "app" / "models" / "registry.py").exists()

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
    assert "class UserUpdate(BaseModel):" in content
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


def test_make_repository_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    init_result = runner.invoke(app, ["init"], input="1\n")
    assert init_result.exit_code == 0

    model_dir = tmp_path / "app" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "user.py").touch()

    result = runner.invoke(app, ["make:repository", "User"])

    assert result.exit_code == 0
    assert "Repository created" in result.stdout

    repo_path = tmp_path / "app" / "repositories" / "user.py"

    assert repo_path.exists()

    content = repo_path.read_text(encoding="utf-8")
    assert "class UserRepository:" in content


def test_make_repository_command_does_not_overwrite(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    init_result = runner.invoke(app, ["init"], input="1\n")
    assert init_result.exit_code == 0

    model_dir = tmp_path / "app" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "user.py").touch()

    first_result = runner.invoke(app, ["make:repository", "User"])

    assert first_result.exit_code == 0

    second_result = runner.invoke(app, ["make:repository", "User"])

    assert second_result.exit_code == 1
    assert "File already exists" in second_result.output


def test_make_repository_requires_model(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    init_result = runner.invoke(app, ["init"], input="1\n")
    assert init_result.exit_code == 0

    result = runner.invoke(app, ["make:repository", "User"])

    assert result.exit_code == 1
    assert "Model file not found" in result.output
    assert "fastisan make:model User" in result.output


def test_make_repository_rejects_project_without_orm(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    init_result = runner.invoke(app, ["init"], input="2\n")
    assert init_result.exit_code == 0

    result = runner.invoke(app, ["make:repository", "User"])

    assert result.exit_code == 1
    assert "requires an ORM" in result.output


def test_make_middleware_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["make:middleware", "User"])

    assert result.exit_code == 0
    assert "Middleware created" in result.stdout

    middleware_path = tmp_path / "app" / "middleware" / "user.py"

    assert middleware_path.exists()

    content = middleware_path.read_text(encoding="utf-8")
    assert "class UserMiddleware:" in content


def test_make_middleware_command_does_not_overwrite(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    first_result = runner.invoke(app, ["make:middleware", "User"])

    assert first_result.exit_code == 0

    second_result = runner.invoke(app, ["make:middleware", "User"])

    assert second_result.exit_code == 1
    assert "File already exists" in second_result.output


def test_make_resource_command_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    init_result = runner.invoke(app, ["init"], input="1\n")
    assert init_result.exit_code == 0

    result = runner.invoke(app, ["make:resource", "User"])
    assert result.exit_code == 0
    assert "Resource created: User" in result.stdout
    assert "Created: " in result.stdout

    assert (tmp_path / "app" / "models" / "user.py").exists()
    assert (tmp_path / "app" / "schemas" / "user.py").exists()
    assert (tmp_path / "app" / "repositories" / "user.py").exists()
    assert (tmp_path / "app" / "services" / "user.py").exists()
    assert (tmp_path / "app" / "routers" / "user.py").exists()

    registry_path = tmp_path / "app" / "routers" / "registry.py"
    registry_content = registry_path.read_text(encoding="utf-8")
    assert "from app.routers.user import router as user_router" in registry_content
    assert "router.include_router(user_router)" in registry_content

    model_registry_path = tmp_path / "app" / "models" / "registry.py"
    model_registry_content = model_registry_path.read_text(encoding="utf-8")
    assert "from app.models.user import User" in model_registry_content
    assert '"User",' in model_registry_content


def test_make_resource_uninitialized(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["make:resource", "User"])
    assert result.exit_code == 1
    assert "not initialized" in result.output


def test_make_resource_orm_none(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    init_result = runner.invoke(app, ["init"], input="2\n")
    assert init_result.exit_code == 0

    result = runner.invoke(app, ["make:resource", "User"])
    assert result.exit_code == 1
    assert "requires an ORM" in result.output


def test_make_resource_existing_component(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    init_result = runner.invoke(app, ["init"], input="1\n")
    assert init_result.exit_code == 0

    services_dir = tmp_path / "app" / "services"
    services_dir.mkdir(parents=True, exist_ok=True)
    (services_dir / "user.py").touch()

    result = runner.invoke(app, ["make:resource", "User"])
    assert result.exit_code == 1
    assert "Resource components already exist" in result.output

    assert not (tmp_path / "app" / "models" / "user.py").exists()


def test_make_resource_duplicate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    init_result = runner.invoke(app, ["init"], input="1\n")
    assert init_result.exit_code == 0

    first_result = runner.invoke(app, ["make:resource", "User"])
    assert first_result.exit_code == 0

    second_result = runner.invoke(app, ["make:resource", "User"])
    assert second_result.exit_code == 1
    assert "Resource components already exist" in second_result.output
