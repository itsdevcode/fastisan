from pathlib import Path

import pytest

from fastisan.generators.model.factory import generate_model


def test_generate_sqlalchemy_model(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    file_path = generate_model("User", "sqlalchemy")

    assert file_path == tmp_path / "app" / "models" / "user.py"
    assert file_path.exists()

    content = file_path.read_text(encoding="utf-8")

    assert "class User(Base):" in content
    assert '__tablename__ = "users"' in content
    assert "id: Mapped[int]" in content
    assert content.endswith("\n")


def test_generate_sqlalchemy_model_uses_snake_case(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    file_path = generate_model("BlogPost", "sqlalchemy")
    content = file_path.read_text(encoding="utf-8")

    assert file_path.name == "blog_post.py"
    assert "class BlogPost(Base):" in content
    assert '__tablename__ = "blog_posts"' in content
    assert content.endswith("\n")


def test_generate_model_without_orm() -> None:
    with pytest.raises(ValueError, match="requires an ORM"):
        _ = generate_model("User", "none")


def test_generate_model_rejects_unsupported_orm() -> None:
    with pytest.raises(ValueError, match="Unsupported ORM"):
        _ = generate_model("User", "django")


def test_generate_sqlalchemy_model_normalizes_class_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    file_path = generate_model("user", "sqlalchemy")
    content = file_path.read_text(encoding="utf-8")

    assert file_path.name == "user.py"
    assert "class User(Base):" in content
    assert '__tablename__ = "users"' in content


def test_generate_sqlalchemy_model_formatting(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    file_path = generate_model("User", "sqlalchemy")
    content = file_path.read_text(encoding="utf-8")

    # Exactly one trailing newline at EOF
    assert content.endswith("\n")
    assert not content.endswith("\n\n")

    # No 3+ consecutive blank lines anywhere (2 blank lines before top-level class is PEP 8)
    assert "\n\n\n\n" not in content

    # Clean consecutive fields without spurious blank lines
    assert (
        "\n    id: Mapped[int] = mapped_column(Integer, primary_key=True)\n    created_at: Mapped[datetime]"
        in content
    )
    assert (
        "\n    created_at: Mapped[datetime] = mapped_column(\n        DateTime, server_default=func.now()\n    )\n    updated_at: Mapped[datetime]"
        in content
    )

    # Clean import grouping
    assert (
        "from datetime import datetime\n\nfrom sqlalchemy import DateTime, Integer, func\nfrom sqlalchemy.orm import Mapped, mapped_column\n\nfrom app.db.base import Base\n\n\nclass User(Base):"
        in content
    )


def test_generate_sqlalchemy_model_with_fields_formatting(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    from fastisan.generators.model.sqlalchemy import SQLAlchemyModelGenerator
    from fastisan.specs import parse_fields

    fields = parse_fields("name:str,age:int?,email:str")
    generator = SQLAlchemyModelGenerator()
    file_path = generator.generate("User", fields=fields)
    content = file_path.read_text(encoding="utf-8")

    # Exactly one trailing newline
    assert content.endswith("\n")
    assert not content.endswith("\n\n")
    assert "\n\n\n\n" not in content

    # All fields must be consecutive with no blank lines between them
    expected_fields_block = (
        "    id: Mapped[int] = mapped_column(Integer, primary_key=True)\n"
        "    name: Mapped[str] = mapped_column(String, nullable=False)\n"
        "    age: Mapped[int | None] = mapped_column(Integer, nullable=True)\n"
        "    email: Mapped[str] = mapped_column(String, nullable=False)\n"
        "    created_at: Mapped[datetime] = mapped_column("
    )
    assert expected_fields_block in content
