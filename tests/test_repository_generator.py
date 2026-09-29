from pathlib import Path

import pytest

from fastisan.generators.repository import RepositoryGenerator


def test_repository_generator_creates_repository_without_model(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    generator = RepositoryGenerator()
    file_path = generator.generate("User", "sqlalchemy")

    assert file_path == tmp_path / "app" / "repositories" / "user.py"
    assert file_path.exists()

    content = file_path.read_text(encoding="utf-8")

    assert "class UserRepository:" in content
    assert "async def list(self)" not in content
    assert "pass" in content


def test_repository_generator_creates_sqlalchemy_repository(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    
    # Create mock model file
    model_dir = tmp_path / "app" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "user.py").touch()

    generator = RepositoryGenerator()
    file_path = generator.generate("User", "sqlalchemy")

    content = file_path.read_text(encoding="utf-8")

    assert "class UserRepository:" in content
    assert "async def list(self) -> list[User]:" in content
    assert "async def detail(self, id: int) -> User | None:" in content
    assert "async def create(self, **kwargs: Any) -> User:" in content
    assert "from app.models.user import User" in content


def test_repository_generator_normalizes_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    generator = RepositoryGenerator()
    file_path = generator.generate("blog_post", "sqlalchemy")

    assert file_path == tmp_path / "app" / "repositories" / "blog_post.py"


def test_repository_generator_does_not_overwrite_existing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    generator = RepositoryGenerator()
    _ = generator.generate("User", "sqlalchemy")

    with pytest.raises(FileExistsError):
        _ = generator.generate("User", "sqlalchemy")
