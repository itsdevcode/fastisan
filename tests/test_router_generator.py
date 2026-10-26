from pathlib import Path

import pytest

from fastisan.generators.router import generate_router


def test_generate_router(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test fallback router generation when no schema/service exists."""
    monkeypatch.chdir(tmp_path)

    file_path = generate_router("BlogPost")

    assert file_path == tmp_path / "app" / "routers" / "blog_post.py"
    assert file_path.exists()

    content = file_path.read_text(encoding="utf-8")

    assert 'prefix="/blog_post"' in content
    assert 'tags=["BlogPost"]' in content
    assert "UserService" not in content
    assert "async def index():" in content
    assert "message" in content


def test_generate_router_schema_no_service(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    schema_dir = tmp_path / "app" / "schemas"
    schema_dir.mkdir(parents=True, exist_ok=True)
    (schema_dir / "user.py").touch()

    file_path = generate_router("User")
    content = file_path.read_text(encoding="utf-8")

    assert "UserService" not in content
    assert "UserCreate" not in content
    assert "async def index():" in content


def test_generate_router_service_no_schema(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    service_dir = tmp_path / "app" / "services"
    service_dir.mkdir(parents=True, exist_ok=True)
    (service_dir / "user.py").touch()

    file_path = generate_router("User")
    content = file_path.read_text(encoding="utf-8")

    assert "UserService" not in content
    assert "UserCreate" not in content
    assert "async def index():" in content


def test_generate_router_schema_and_service(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    schema_dir = tmp_path / "app" / "schemas"
    schema_dir.mkdir(parents=True, exist_ok=True)
    (schema_dir / "user.py").touch()

    service_dir = tmp_path / "app" / "services"
    service_dir.mkdir(parents=True, exist_ok=True)
    (service_dir / "user.py").touch()

    file_path = generate_router("User")
    content = file_path.read_text(encoding="utf-8")

    assert "from app.services.user import UserService" in content
    assert (
        "from app.schemas.user import UserCreate, UserResponse, UserUpdate" in content
    )
    assert "def get_user_service() -> UserService:" in content
    assert "raise NotImplementedError" in content
    assert "async def list_users(" in content
    assert "async def get_user(" in content
    assert "async def create_user(" in content
    assert "async def update_user(" in content
    assert "async def delete_user(" in content
    assert "status.HTTP_404_NOT_FOUND" in content
    assert "status.HTTP_201_CREATED" in content
    assert "status.HTTP_204_NO_CONTENT" in content
    assert "await service.list()" in content
    assert "await service.detail(id)" in content
    assert "await service.create(data)" in content
    assert "await service.update(id, data)" in content
    assert "await service.delete(id)" in content


def test_generate_router_complete_composition(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    schema_dir = tmp_path / "app" / "schemas"
    schema_dir.mkdir(parents=True, exist_ok=True)
    (schema_dir / "user.py").touch()

    service_dir = tmp_path / "app" / "services"
    service_dir.mkdir(parents=True, exist_ok=True)
    (service_dir / "user.py").touch()

    repo_dir = tmp_path / "app" / "repositories"
    repo_dir.mkdir(parents=True, exist_ok=True)
    (repo_dir / "user.py").touch()

    db_dir = tmp_path / "app" / "db"
    db_dir.mkdir(parents=True, exist_ok=True)
    (db_dir / "session.py").touch()

    file_path = generate_router("User")
    content = file_path.read_text(encoding="utf-8")

    assert "from sqlalchemy.ext.asyncio import AsyncSession" in content
    assert "from app.db.session import get_session" in content
    assert "from app.repositories.user import UserRepository" in content
    assert "from app.services.user import UserService" in content
    assert "def get_user_service(" in content
    assert "session: AsyncSession = Depends(get_session)," in content
    assert "repository = UserRepository(session)" in content
    assert "return UserService(repository)" in content
    assert "raise NotImplementedError" not in content


def test_generate_router_does_not_overwrite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _ = generate_router("User")
    with pytest.raises(FileExistsError):
        _ = generate_router("User")


def test_generate_router_formatting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    # 1. Minimal router
    min_file = generate_router("User")
    min_content = min_file.read_text(encoding="utf-8")

    assert min_content.startswith("from fastapi import APIRouter")
    assert min_content.endswith("\n")
    assert not min_content.endswith("\n\n")
    assert "\n\n\n\n" not in min_content

    # 2. Full CRUD router
    app_dir = tmp_path / "app"
    schemas_dir = app_dir / "schemas"
    schemas_dir.mkdir(parents=True, exist_ok=True)
    (schemas_dir / "user.py").touch()

    services_dir = app_dir / "services"
    services_dir.mkdir(parents=True, exist_ok=True)
    (services_dir / "user.py").touch()

    repos_dir = app_dir / "repositories"
    repos_dir.mkdir(parents=True, exist_ok=True)
    (repos_dir / "user.py").touch()

    db_dir = app_dir / "db"
    db_dir.mkdir(parents=True, exist_ok=True)
    (db_dir / "session.py").touch()

    min_file.unlink()
    full_file = generate_router("User")
    full_content = full_file.read_text(encoding="utf-8")

    assert full_content.startswith(
        "from fastapi import APIRouter, Depends, HTTPException, status"
    )
    assert full_content.endswith("\n")
    assert not full_content.endswith("\n\n")
    assert "\n\n\n\n" not in full_content
