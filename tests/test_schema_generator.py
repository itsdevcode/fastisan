from pathlib import Path

import pytest

from fastisan.generators.schema import SchemaGenerator


def test_schema_generator_creates_schema(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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


def test_schema_generator_formatting_empty_and_populated(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    generator = SchemaGenerator()

    # 1. Empty fields schema
    empty_file = generator.generate("User")
    empty_content = empty_file.read_text(encoding="utf-8")

    assert empty_content.endswith("\n")
    assert not empty_content.endswith("\n\n")
    assert "\n\n\n\n" not in empty_content

    assert (
        "from datetime import datetime\nfrom pydantic import BaseModel, ConfigDict\n\n\nclass UserBase(BaseModel):\n    pass\n\n\nclass UserCreate(UserBase):\n    pass\n\n\nclass UserUpdate(BaseModel):\n    pass\n\n\nclass UserResponse(UserBase):"
        in empty_content
    )

    # 2. Populated fields schema
    from fastisan.specs import parse_fields

    fields = parse_fields("name:str,age:int?")

    # Remove previous to generate populated
    empty_file.unlink()
    pop_file = generator.generate("User", fields=fields)
    pop_content = pop_file.read_text(encoding="utf-8")

    assert pop_content.endswith("\n")
    assert not pop_content.endswith("\n\n")
    assert "\n\n\n\n" not in pop_content

    # Fields inside UserBase are consecutive
    assert (
        "class UserBase(BaseModel):\n    name: str\n    age: int | None = None\n\n\nclass UserCreate(UserBase):"
        in pop_content
    )
    # Fields inside UserUpdate are consecutive
    assert (
        "class UserUpdate(BaseModel):\n    name: str | None = None\n    age: int | None = None\n\n\nclass UserResponse(UserBase):"
        in pop_content
    )
