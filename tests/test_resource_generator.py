from pathlib import Path

import pytest

from fastisan.generators.resource import generate_resource


def test_generate_sqlalchemy_resource(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    from fastisan.generators.database.factory import generate_database_foundation

    _ = generate_database_foundation("sqlalchemy")

    paths = generate_resource("User", "sqlalchemy")

    assert len(paths) == 5

    expected_paths = [
        tmp_path / "app" / "models" / "user.py",
        tmp_path / "app" / "schemas" / "user.py",
        tmp_path / "app" / "repositories" / "user.py",
        tmp_path / "app" / "services" / "user.py",
        tmp_path / "app" / "routers" / "user.py",
    ]

    for p in expected_paths:
        assert p.exists()

    router_content = expected_paths[4].read_text(encoding="utf-8")
    assert "from app.services.user import UserService" in router_content
    assert "Depends(get_user_service)" in router_content
    assert "from sqlalchemy.ext.asyncio import AsyncSession" in router_content
    assert "repository = UserRepository(session)" in router_content
    assert "raise NotImplementedError" not in router_content

    service_content = expected_paths[3].read_text(encoding="utf-8")
    assert "from app.repositories.user import UserRepository" in service_content


def test_resource_name_normalization_lowercase(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    _ = generate_resource("user", "sqlalchemy")

    assert (tmp_path / "app" / "models" / "user.py").exists()
    assert (tmp_path / "app" / "schemas" / "user.py").exists()
    assert (tmp_path / "app" / "repositories" / "user.py").exists()
    assert (tmp_path / "app" / "services" / "user.py").exists()
    assert (tmp_path / "app" / "routers" / "user.py").exists()


def test_resource_name_normalization_snake_case(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    _ = generate_resource("blog_post", "sqlalchemy")

    assert (tmp_path / "app" / "models" / "blog_post.py").exists()
    assert (tmp_path / "app" / "schemas" / "blog_post.py").exists()
    assert (tmp_path / "app" / "repositories" / "blog_post.py").exists()
    assert (tmp_path / "app" / "services" / "blog_post.py").exists()
    assert (tmp_path / "app" / "routers" / "blog_post.py").exists()


def test_resource_generation_fails_orm_none(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="requires an ORM"):
        _ = generate_resource("User", "none")

    assert not (tmp_path / "app").exists()


def test_resource_generation_fails_unsupported_orm(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="Unsupported ORM: unknown"):
        _ = generate_resource("User", "unknown")

    assert not (tmp_path / "app").exists()


def test_preflight_atomicity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    services_dir = tmp_path / "app" / "services"
    services_dir.mkdir(parents=True, exist_ok=True)
    service_file = services_dir / "user.py"
    _ = service_file.write_text("KEEP ME", encoding="utf-8")

    with pytest.raises(FileExistsError, match="components already exist"):
        _ = generate_resource("User", "sqlalchemy")

    assert service_file.read_text(encoding="utf-8") == "KEEP ME"

    assert not (tmp_path / "app" / "models" / "user.py").exists()
    assert not (tmp_path / "app" / "schemas" / "user.py").exists()
    assert not (tmp_path / "app" / "repositories" / "user.py").exists()
    assert not (tmp_path / "app" / "routers" / "user.py").exists()


def test_duplicate_resource_generation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    _ = generate_resource("User", "sqlalchemy")

    with pytest.raises(FileExistsError):
        _ = generate_resource("User", "sqlalchemy")
