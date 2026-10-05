from pathlib import Path

import pytest

from fastisan.generators.schema import SchemaGenerator


def test_schema_generator_creates_schema(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    generator = SchemaGenerator()
    file_path = generator.generate("User")

    assert file_path == tmp_path / "app" / "schemas" / "user.py"
    assert file_path.exists()

    content = file_path.read_text(encoding="utf-8")

    assert "class UserBase(BaseModel):" in content
    assert "class UserCreate(UserBase):" in content
    assert "class UserUpdate(BaseModel):" in content
    assert "class UserResponse(UserBase):" in content
    assert "model_config = ConfigDict(from_attributes=True)" in content


def test_schema_generator_normalizes_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    generator = SchemaGenerator()
    file_path = generator.generate("blog_post")

    assert file_path == tmp_path / "app" / "schemas" / "blog_post.py"

    content = file_path.read_text(encoding="utf-8")

    assert "class BlogPostBase(BaseModel):" in content
    assert "class BlogPostCreate(BlogPostBase):" in content
    assert "class BlogPostUpdate(BaseModel):" in content
    assert "class BlogPostResponse(BlogPostBase):" in content


def test_schema_generator_does_not_overwrite_existing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    generator = SchemaGenerator()
    _ = generator.generate("User")

    with pytest.raises(FileExistsError):
        _ = generator.generate("User")