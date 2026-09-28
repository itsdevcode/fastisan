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