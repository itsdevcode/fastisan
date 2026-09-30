from pathlib import Path

import pytest

from fastisan.generators.repository import generate_repository


def test_repository_generation_fails_without_model(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError, match="Model file not found"):
        _ = generate_repository("User", "sqlalchemy")

    assert not (tmp_path / "app" / "repositories" / "user.py").exists()


def test_repository_generator_creates_sqlalchemy_repository(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    model_dir = tmp_path / "app" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "user.py").touch()

    file_path = generate_repository("User", "sqlalchemy")

    content = file_path.read_text(encoding="utf-8")

    assert "class UserRepository:" in content
    assert "async def list(self) -> list[User]:" in content
    assert "async def detail(self, id: int) -> User | None:" in content
    assert "async def create(self, **kwargs: Any) -> User:" in content
    assert "from app.models.user import User" in content


def test_repository_generation_fails_for_orm_none(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="Repository generation requires an ORM"):
        _ = generate_repository("User", "none")


def test_repository_generation_fails_for_unsupported_orm(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="Unsupported ORM: fake_orm"):
        _ = generate_repository("User", "fake_orm")


def test_repository_generator_normalizes_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    model_dir = tmp_path / "app" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "blog_post.py").touch()

    file_path = generate_repository("blog_post", "sqlalchemy")

    assert file_path == tmp_path / "app" / "repositories" / "blog_post.py"


def test_repository_generator_does_not_overwrite_existing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    model_dir = tmp_path / "app" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "user.py").touch()

    _ = generate_repository("User", "sqlalchemy")

    with pytest.raises(FileExistsError):
        _ = generate_repository("User", "sqlalchemy")
