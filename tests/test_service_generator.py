from pathlib import Path

import pytest

from fastisan.generators.service import ServiceGenerator


def test_service_generator_creates_service_without_schema(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    generator = ServiceGenerator()
    file_path = generator.generate("User")

    assert file_path == tmp_path / "app" / "services" / "user.py"
    assert file_path.exists()

    content = file_path.read_text(encoding="utf-8")

    assert "class UserService:" in content
    assert "async def list(self)" not in content
    assert "pass" in content


def test_service_generator_creates_service_with_schema(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    
    # Create a mock schema file so the generator detects it
    schema_dir = tmp_path / "app" / "schemas"
    schema_dir.mkdir(parents=True, exist_ok=True)
    (schema_dir / "user.py").touch()

    generator = ServiceGenerator()
    file_path = generator.generate("User")

    content = file_path.read_text(encoding="utf-8")

    assert "class UserService:" in content
    assert "async def list(self) -> list[UserResponse]:" in content
    assert "async def detail(self, id: int) -> UserResponse | None:" in content
    assert "async def create(self, data: UserCreate) -> UserResponse:" in content
    assert "raise NotImplementedError" in content
    assert "from app.schemas.user import UserCreate, UserResponse, UserUpdate" in content


def test_service_generator_normalizes_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    generator = ServiceGenerator()
    file_path = generator.generate("blog_post")

    assert file_path == tmp_path / "app" / "services" / "blog_post.py"

    content = file_path.read_text(encoding="utf-8")

    assert "class BlogPostService:" in content
    assert "pass" in content


def test_service_generator_does_not_overwrite_existing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    generator = ServiceGenerator()
    _ = generator.generate("User")

    with pytest.raises(FileExistsError):
        _ = generator.generate("User")
